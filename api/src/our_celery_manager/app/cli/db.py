import typer

db_cli = typer.Typer()

from our_celery_manager.app.startup_checks import pre_startup_db_migration


@db_cli.command()
def upgrade_ddl():
    pre_startup_db_migration()
