# Allow forward references in type hints (helps when classes reference each other
# before they are defined). Not strictly needed here, but often added in modern Python projects.
from __future__ import annotations

# Typer is a library for building CLI (Command Line Interface) apps.
# It makes it easy to create commands with arguments and options.
import typer

# Optional typing support: lets you mark arguments as Optional[T] (i.e., can be None).
# Not used in this file yet, but can be useful when extending CLI with more commands.
from typing import Optional

# Import the seeding function we already wrote in app/seeds/seed_users.py.
# This function creates default users (super_admin, editor, subscriber).
from app.seeds.seed_users import seed_users  # reuse the function

# asyncio is Python’s built-in library for running asynchronous code.
# Our seed_users() function is async, so we need asyncio.run() to call it
# inside this synchronous CLI context.
import asyncio


# Create a Typer application instance.
# Think of this as the root command group (like `artisan` in Laravel or `django-admin` in Django).
# All subcommands will be registered to this "app".
app = typer.Typer(help="Management CLI")


# Define a new CLI command called `seed:users`.
# The string "seed:users" becomes the subcommand name you run on the terminal:
#   python -m app.management.cli seed:users
@app.command("seed:users")
def seed_users_cmd():
    """
    Seed default users (super_admin, editor, subscriber).

    When run, this command will:
    - Open a DB session
    - Insert super_admin, editor, and subscriber accounts if they don’t exist
    - Print how many users were created vs skipped
    """
    # Run the async seeding function in a synchronous context.
    # asyncio.run() starts a new event loop, executes the coroutine, and waits for it to finish.
    res = asyncio.run(seed_users())

    # Print the result to the console.
    # res is a dict like {"created": 3, "skipped": 0}.
    typer.echo(f"Users created: {res['created']}, skipped: {res['skipped']}")


# This ensures the CLI app runs only if the file is executed directly
# (e.g., `python app/management/cli.py`).
# If the file is imported elsewhere, this block won’t run.
if __name__ == "__main__":
    app()
