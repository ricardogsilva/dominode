import logging
from pathlib import Path
from time import sleep
from urllib3.exceptions import MaxRetryError

import docker
import pytest
import sqlalchemy as sla
from minio import Minio
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope='session')
def db_users_credentials():
    return {
        'ppd_editor1': ('ppd_editor1', ['ppd_editor', 'admin']),
        'ppd_editor2': ('ppd_editor2', ['ppd_editor']),
        'ppd_user1': ('ppd_user1', ['ppd_user']),
        'ppd_user2': ('ppd_user2', ['ppd_user']),
        'lsd_editor1': ('lsd_editor1', ['lsd_editor']),
        'lsd_editor2': ('lsd_editor2', ['lsd_editor']),
        'lsd_user1': ('lsd_user1', ['lsd_user']),
        'lsd_user2': ('lsd_user2', ['lsd_user']),
    }


@pytest.fixture(scope='session')
def db_admin_credentials():
    return {
        'host': 'localhost',
        'db': 'dominode_pytest',
        'port': '55432',
        'user': 'dominode_test',
        'password': 'dominode_test',
    }


@pytest.fixture(scope='session')
def docker_client():
    return docker.from_env()


@pytest.fixture(scope='session')
def db_container(docker_client, db_admin_credentials):
    container = docker_client.containers.run(
        'postgis/postgis:12-3.0-alpine',
        detach=True,
        name=db_admin_credentials['db'],
        remove=True,
        ports={
            '5432': db_admin_credentials['port']
        },
        environment={
            'POSTGRES_DB': db_admin_credentials['db'],
            'POSTGRES_USER': db_admin_credentials['user'],
            'POSTGRES_PASSWORD': db_admin_credentials['password'],
        }

    )
    yield container
    logger.info(f'Removing container...')
    container.stop()


@pytest.fixture(scope='session')
def db_connection(db_container, db_admin_credentials):
    engine = sla.create_engine('postgresql://{user}:{password}@{host}:{port}/{db}'.format(
        user=db_admin_credentials['user'],
        password=db_admin_credentials['password'],
        host=db_admin_credentials['host'],
        port=db_admin_credentials['port'],
        db=db_admin_credentials['db']
    ))
    connected = False
    max_tries = 30
    current_try = 0
    sleep_for = 2  # seconds
    while not connected and current_try < max_tries:
        try:
            with engine.connect() as connection:
                connected = True
                yield connection
                logger.info('Closing DB connection...')
        except OperationalError:
            print(f'Could not connect to DB ({current_try + 1}/{max_tries})')
            current_try += 1
            if current_try < max_tries:
                sleep(sleep_for)
            else:
                raise


@pytest.fixture(scope='session')
def bootstrapped_db_connection(db_connection):
    bootstrap_sql_path = REPO_ROOT / 'sql/bootstrap-db.sql'
    raw_connection = db_connection.connection
    raw_cursor = raw_connection.cursor()
    raw_cursor.execute(bootstrap_sql_path.read_text())
    raw_connection.commit()
    return db_connection


@pytest.fixture(scope='session')
def db_users(bootstrapped_db_connection, db_users_credentials):
    for user, user_info in db_users_credentials.items():
        password, roles = user_info
        bootstrapped_db_connection.execute(
            f'CREATE USER {user} PASSWORD \'{password}\' IN ROLE {", ".join(roles)}')
    return bootstrapped_db_connection


@pytest.fixture(scope='session')
def minio_server_info():
    return {
        'name': 'minio-server-pytest',
        'host': 'localhost',
        'port': '9100',
        'access_key': 'myuser',
        'secret_key': 'mypassword',
    }


@pytest.fixture(scope='session')
def minio_server(docker_client, minio_server_info):
    container = docker_client.containers.run(
        'minio/minio',
        detach=True,
        name=minio_server_info['name'],
        remove=True,
        network='host',
        ports={
            '9000': minio_server_info['port']
        },
        environment={
            'MINIO_ACCESS_KEY': minio_server_info['access_key'],
            'MINIO_SECRET_KEY': minio_server_info['secret_key'],
        }

    )
    yield container
    logger.info(f'Removing container...')
    container.stop()


@pytest.fixture(scope='session')
def minio_client(minio_server, minio_server_info):
    connected = False
    max_tries = 30
    current_try = 0
    sleep_for = 2  # seconds
    while not connected and current_try < max_tries:
        try:
            client = Minio(
                f'{minio_server_info["host"]}:{minio_server_info["port"]}',
                access_key=minio_server_info['access_key'],
                secret_key=minio_server_info['secret_key'],
                secure=False
            )
            break
        except MaxRetryError:
            print(f'Could not connect to minIO server ({current_try + 1}/{max_tries})')
            current_try += 1
            if current_try < max_tries:
                sleep(sleep_for)
            else:
                raise
    return client
