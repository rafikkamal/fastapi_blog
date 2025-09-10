from __future__ import annotations
import typer
from typing import Optional
from app.seeds.seed_users import seed_users  # reuse the function
import asyncio

app = typer.Typer(help="Management CLI")

@app.command("seed:users")
def seed_users_cmd():
    """Seed default users (super_admin, editor, subscriber)."""
    res = asyncio.run(seed_users())
    typer.echo(f"Users created: {res['created']}, skipped: {res['skipped']}")

if __name__ == "__main__":
    app()
