"""Extra admin commands to manage the DomiNode database server

This script adds some functions to perform DomiNode related tasks in a more
expedite manner than using the bare `psql` client

"""

import typing
from configparser import ConfigParser
from contextlib import contextmanager
from pathlib import Path
from time import sleep

import sqlalchemy as sla
import typer
from sqlalchemy.exc import OperationalError

from .constants import (
    DepartmentName,
    UserRole,
)

_help_intro = 'Manage postgis database'

app = typer.Typer(
    short_help=_help_intro,
    help=_help_intro
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_DIR = Path('~/.pg_service.conf').expanduser()


@app.command()
def bootstrap(
        db_service_name: str,
        db_service_file: Path = DEFAULT_CONFIG_DIR
):
    """Perform initial bootstrap of the database

    This function will take care of creating the relevant schemas, group roles
    and access controls for using the postgis database for DomiNode.

    """
    db_url = load_postgres_service(db_service_name, db_service_file.read_text())
    bootstrap_sql_path = REPO_ROOT / 'sql/bootstrap-db.sql'
    with get_db_connection(db_url) as db_connection:
        raw_connection = db_connection.connection
        raw_cursor = raw_connection.cursor()
        typer.echo('Bootstrapping db...')
        raw_cursor.execute(bootstrap_sql_path.read_text())
        raw_connection.commit()


@app.command()
def add_department_user(
        db_service_name: str,
        username: str,
        password: str,
        department: DepartmentName,
        role: typing.Optional[UserRole] = UserRole.REGULAR_DEPARTMENT_USER,
        db_service_file: Path = DEFAULT_CONFIG_DIR
):
    db_url = load_postgres_service(db_service_name, db_service_file.read_text())
    sql_role = {
        UserRole.EDITOR: f'{department.value}_editor',
        UserRole.REGULAR_DEPARTMENT_USER: f'{department.value}_user',
    }[role]
    with get_db_connection(db_url) as db_connection:
        raw_connection = db_connection.connection
        raw_cursor = raw_connection.cursor()
        typer.echo(f'Creating user {username}...')
        raw_cursor.execute(
            f'CREATE USER {username} PASSWORD \'{password}\' IN ROLE {sql_role}'
        )
        raw_connection.commit()


@contextmanager
def get_db_connection(db_url: str):
    engine = sla.create_engine(db_url)
    connected = False
    max_tries = 30
    current_try = 0
    sleep_for = 2  # seconds
    while not connected and current_try < max_tries:
        try:
            with engine.connect() as connection:
                connected = True
                yield connection
        except OperationalError:
            print(f'Could not connect to DB ({current_try + 1}/{max_tries})')
            current_try += 1
            if current_try < max_tries:
                sleep(sleep_for)
            else:
                raise


def load_postgres_service(
        service:str,
        service_file_contents: str
) -> str:
    config = ConfigParser()
    config.read_string(service_file_contents)
    section = config[service]
    return (
        f'postgresql://{section["user"]}:{section["password"]}@'
        f'{section["host"]}:{section.get("port", 5432)}/'
        f'{section["dbname"]}'
    )


def parse_postgres_service(service: typing.MutableMapping) -> str:
    pass