import sys
from asyncio import CancelledError, TaskGroup
from time import time

import dagger
from dagger import dag, function, object_type

PYTHON_VERSION = "3.12-slim-bullseye"
GUNICORN_CMD = ["gunicorn", "--chdir", "./src", "--bind", ":8000", "--workers", "2", "spokanetech.wsgi"]


@object_type
class SpokaneTech:
    src: dagger.Directory
    req: dagger.File

    def base_container(self) -> dagger.Container:
        """
        The base container that all other containers are built off of.
        """
        return (
            dag.container()
            .from_(f"python:{PYTHON_VERSION}")
            .with_env_variable("PYTHONDONTWRITEBYTECODE", "1")
            .with_env_variable("PYTHONUNBUFFERED", "1")
            # Default Env vars
            .with_env_variable("DJANGO_SETTINGS_MODULE", "spokanetech.settings")
            .with_(env_variables())
            .with_exposed_port(8000)
            .with_file("/tmp/requirements.txt", self.req)
            .with_exec(["pip", "install", "--upgrade", "pip"])
            .with_exec(["pip", "install", "-r", "/tmp/requirements.txt"])
            .with_exec(["rm", "-rf", "/root/.cache"])
            .with_directory("/code/src", self.src)
            .with_workdir("/code")
        )

    @function
    async def dev(self, run: bool = False, fresh_database: bool = False) -> dagger.Container:
        """
        A container that represents the dev environment.
        Celery (and Redis) services are started and attached.
        An Admin user with username/password 'dagger'/'dagger' is created.

        If `--run` is passed, the Django server will be started.
        """
        if fresh_database:
            await self.wipe_db_cache()
        ctr = (
            self.base_container()
            .with_workdir("/code/src")
            # Need to make sure to run the migrations if the database was wiped
            .with_env_variable("CACHEBUSTER", str(time()) if fresh_database else "")
            .with_service_binding("postgres", self.postgres())
            .with_exec(["python", "manage.py", "migrate"])
            .with_exec(["python", "manage.py", "add_superuser", "--username", "dagger", "--password", "dagger"])
            .with_service_binding("redis", self.redis())
            .with_service_binding("celery", self.celery())
        )
        if run:
            ctr = ctr.with_exec(["python", "manage.py", "runserver", "0.0.0.0:8000"])
        return ctr

    @function
    def prod(self) -> dagger.Container:
        """
        A production-ready container.

        Used to deploy to Fly.io.
        """
        return (
            self.base_container()
            .with_(env_variables(SPOKANE_TECH_DEV=""))  # Override other envrionment variables in Fly.io prod.
            .with_exec(GUNICORN_CMD)
        )

    async def wipe_db_cache(self) -> str:
        return await (
            dag.container()
            .from_("alpine")
            .with_env_variable("CACHEBUSTER", str(time()))
            .with_mounted_cache("/cache", dag.cache_volume("postgresql"))
            .with_exec(["sh", "-c", "rm -rf /cache/*"])
            .stdout()
        )

    def redis(self) -> dagger.Service:
        return dag.container().from_("redis:7.2").with_exposed_port(6379).as_service()

    def postgres(self) -> dagger.Service:
        return (
            dag.container()
            .from_("postgres:16")
            .with_mounted_cache("/var/lib/postgresql/data", dag.cache_volume("postgresql"))
            .with_env_variable("POSTGRES_PASSWORD", "dagger")
            .with_env_variable("POSTGRES_USER", "dagger")
            .with_exposed_port(5432)
            .as_service()
        )

    def celery(self) -> dagger.Service:
        return (
            self.base_container()
            .without_exposed_port(8000)
            .with_(env_variables())
            .with_service_binding("postgres", self.postgres())
            .with_service_binding("redis", self.redis())
            .with_exec(
                [
                    "python",
                    "-m",
                    "celery",
                    "--workdir",
                    "./src",
                    "-A",
                    "spokanetech.celery",
                    "worker",
                    "-B",
                    "-l",
                    "INFO",
                ]
            )
            .as_service()
        )

    async def run_linter(self, cmd: list[str], ctr: dagger.Container) -> str:
        """
        Helper function to run linters.
        """
        try:
            return f"Command {' '.join(cmd)} passed!\n{await ctr.with_exec(cmd).stdout()}"
        except dagger.ExecError as e:
            # The ExecError exposes the
            raise LinterError(exec_error=e)

    @function
    async def lint(self, pyproject: dagger.File) -> str:
        """
        Lint using ruff.
        """
        ctr = self.base_container().with_exec(["pip", "install", "ruff"]).with_file("pyproject.toml", pyproject)
        return await self.run_linter(["ruff", "check"], ctr)

    @function
    async def format(self, pyproject: dagger.File) -> str:
        """
        Check if the code is formatted correctly.
        """
        ctr = self.base_container().with_exec(["pip", "install", "ruff"]).with_file("pyproject.toml", pyproject)
        return await self.run_linter(["ruff", "format", "--check"], ctr)

    @function
    async def bandit(self, pyproject: dagger.File) -> str:
        """
        Check for security issues using Bandit.
        """
        ctr = self.base_container().with_exec(["pip", "install", "bandit"]).with_file("pyproject.toml", pyproject)
        return await self.run_linter(["bandit", "-c", "pyproject.toml", "-r", "src"], ctr)

    @function
    async def test(self, pyproject: dagger.File, dev_req: dagger.File) -> str:
        """
        Run tests using Pytest.
        """
        ctr = (
            self.base_container()
            .with_env_variable("CELERY_BROKER_URL", "noop")
            .without_env_variable("DATABASE_URL")  # Use default sqlite
            .with_file("dev_req.txt", dev_req)
            .with_exec(["pip", "install", "-r", "dev_req.txt"])
            .with_file("pyproject.toml", pyproject)
        )
        return await self.run_linter(
            [
                "pytest",
                "-vv",
                "--config-file",
                "pyproject.toml",
                "-k",
                "not integration",
                "src",
            ],
            ctr,
        )

    @function
    async def all_linters(self, pyproject: dagger.File, dev_req: dagger.File, verbose: bool = False) -> str:
        """
        Runs all the liners.
        Pass `--verbose` to not summarize linter output.
        """
        # Run all the linters
        async with TaskGroup() as tg:
            tasks = [
                tg.create_task(self.lint(pyproject)),
                tg.create_task(self.format(pyproject)),
                tg.create_task(self.bandit(pyproject)),
                tg.create_task(self.test(pyproject, dev_req)),
            ]

        # Color Codes
        RESET = "\u001b[0m"
        RED = "\u001b[31m"
        GREEN = "\u001b[32m"
        PASS = f"{GREEN}PASSED!{RESET} "
        FAIL = f"{RED}FAILED!{RESET} "

        # Format the results nicely
        passed = ""
        failed = ""
        for task in tasks:
            try:
                # Task Passed
                result = task.result()
                if not verbose:
                    result = result.splitlines()[0]  # Just grab the first line
                passed += f"{PASS}{result}\n"
            except LinterError as e:
                # Task failed
                failed += f"{FAIL}Command `{' '.join(e.exec_error.command)}` failed with exit code {e.exec_error.exit_code}.\n"
                if verbose:
                    failed += f"stdout:\n{e.exec_error.stdout}\nstderr:\n{e.exec_error.stderr}\n"
        if failed:
            print(f"{passed}\n{failed}")
            sys.exit(1)
        return f"{passed}\n{failed}"

    @function
    def docs(self, mkdocs: dagger.File) -> dagger.Service:
        """
        Run the documentation server locally, without needing to
        install cairo.

        When calling this function use
          `--src ./docs` and `--req ./requirements/dev.txt`.
        """
        return (
            dag.container()
            .from_(f"python:{PYTHON_VERSION}")
            .with_exec(["apt-get", "update"])
            .with_exec(
                [
                    "apt-get",
                    "install",
                    "-y",
                    "libcairo2-dev",
                    "libfreetype6-dev",
                    "libffi-dev",
                    "libjpeg-dev",
                    "libpng-dev",
                    "libz-dev",
                ]
            )
            .with_exposed_port(8000)
            .with_file("/req.txt", self.req)
            .with_exec(["pip", "install", "-r", "req.txt"])
            .with_directory("/docs", self.src)
            .with_file("mkdocs.yaml", mkdocs)
            .with_exec(["mkdocs", "serve", "-a", "0.0.0.0:8000", "--no-livereload"])
            .as_service()
        )


def env_variables(**kwargs):
    """
    Used to add environment variables to a container via the `dagger.Container.with_` function.

    To override or add environment variables pass them as kwargs to the function.
    """
    defaults: dict[str, str] = {
        "SPOKANE_TECH_DEV": "true",
        "DATABASE_URL": "postgres://dagger:dagger@postgres:5432/dagger",
        "USE_AZURE": "false",
        "CELERY_BROKER_URL": "redis://redis:6379/0",
        "DISCORD_WEBHOOK_URL": "",
        "EVENTBRITE_API_TOKEN": "",
    }
    if kwargs is not None:
        defaults.update(kwargs)

    def _env_vars(ctr: dagger.Container) -> dagger.Container:
        for k, v in defaults.items():
            ctr = ctr.with_env_variable(k, v)
        return ctr

    return _env_vars


class LinterError(CancelledError):
    exec_error: dagger.ExecError

    def __init__(self, exec_error):
        self.exec_error = exec_error

    def __str__(self):
        return str(self.exec_error)
