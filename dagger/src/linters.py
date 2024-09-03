import sys
from asyncio import CancelledError, TaskGroup

import dagger
from dagger import function, object_type


@object_type
class Linter:
    ctr: dagger.Container

    async def run_linter(self, cmd: list[str]) -> str:
        """
        Helper function to run linters.
        """
        try:
            return f"Command {' '.join(cmd)} passed!\n{await self.ctr.with_exec(cmd).stdout()}"
        except dagger.ExecError as e:
            # The ExecError exposes the
            raise LinterError(exec_error=e)

    @function
    async def check_django(self) -> str:
        """
        Run Django system checks.
        """
        return await self.run_linter(["src/manage.py", "check"])

    @function
    async def check(self) -> str:
        """
        Flake8 style checks using ruff.
        """
        return await self.run_linter(["ruff", "check"])

    @function
    async def format(self) -> str:
        """
        Check if the code is formatted correctly.
        """
        return await self.run_linter(["ruff", "format", "--check"])

    @function
    async def bandit(self) -> str:
        """
        Check for security issues using Bandit.
        """
        return await self.run_linter(["bandit", "-c", "pyproject.toml", "-r", "src"])

    @function
    async def test(self) -> str:
        """
        Run tests using Pytest.
        """
        self.ctr = (
            self.ctr.with_env_variable("CELERY_BROKER_URL", "noop").without_env_variable(
                "DATABASE_URL"
            )  # Use default sqlite
        )
        return await self.run_linter(
            [
                "pytest",
                "-vv",
                "--config-file",
                "pyproject.toml",
                "src",
            ],
        )

    @function
    async def all(self) -> str:
        """
        Runs all the liners and shows a summary.
        """
        # Run all the linters
        async with TaskGroup() as tg:
            tasks = [
                tg.create_task(self.check_django()),
                tg.create_task(self.check()),
                tg.create_task(self.format()),
                tg.create_task(self.bandit()),
                tg.create_task(self.test()),
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
                result = task.result().splitlines()[0]
                passed += f"{PASS}{result}\n"
            except LinterError as e:
                # Task failed
                failed += f"{FAIL}Command `{' '.join(e.exec_error.command)}` failed with exit code {e.exec_error.exit_code}.\n"
        if failed:
            print(f"{passed}\n{failed}")
            sys.exit(1)
        return f"{passed}\n{failed}"


class LinterError(CancelledError):
    exec_error: dagger.ExecError

    def __init__(self, exec_error):
        self.exec_error = exec_error

    def __str__(self):
        return str(self.exec_error)
