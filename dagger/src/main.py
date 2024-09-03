from time import time
from typing import Annotated

import dagger
from dagger import dag, function, object_type, DefaultPath, Ignore
from linters import Linter

PYTHON_VERSION = "3.12-slim-bullseye"
GUNICORN_CMD = ["gunicorn", "--chdir", "./src", "--bind", ":8000", "--workers", "2", "spokanetech.wsgi"]


@object_type
class SpokaneTech:
    src: dagger.Directory
    is_dev: bool

    def __init__(
        self,
        src: Annotated[
            dagger.Directory,
            DefaultPath("/"),
            Ignore([".venv", "*.sqlite3", ".env*", ".vscode", "DS_Store", "*.dump", ".dagger"]),
        ],
        is_dev: bool = True,
    ):
        self.src = src
        self.is_dev = is_dev
        self.pyproject = self.src.file("pyproject.toml")
        if self.is_dev:
            self.lockfile = self.src.file("requirements.dev.lock")
        else:
            self.lockfile = self.src.file("requirements.lock")

    @function
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
            .with_file("/tmp/requirements.lock", self.lockfile)
            .with_exec(["pip", "install", "--upgrade", "pip"])
            .with_exec(["pip", "install", "-r", "/tmp/requirements.lock"])
            .with_exec(["rm", "-rf", "/root/.cache"])
            .with_directory("/code", self.src)
            .with_workdir("/code")
        )

    @function
    def linters(self) -> Linter:
        return Linter(ctr=self.base_container())  # type: ignore

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
    async def up(self, fresh_database: bool = False) -> dagger.Service:
        """
        Convenience wrapper around `dagger call dev --run as-service up`
        """
        return (await self.dev(run=True, fresh_database=fresh_database)).as_service()

    @function
    def prod(self) -> dagger.Container:
        """
        A production-ready container.
        """
        return (
            self.base_container()
            .with_(env_variables(SPOKANE_TECH_DEV=""))  # Override other envrionment variables in prod.
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

    @function
    def docs(self) -> dagger.Service:
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
            .with_file("/req.txt", self.lockfile)
            .with_exec(["pip", "install", "-r", "req.txt"])
            .with_directory("/docs", self.src.directory("docs"))
            .with_file("mkdocs.yaml", self.src.file("mkdocs.yml"))
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
