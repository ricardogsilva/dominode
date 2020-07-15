"""Commands to bootstrap minIO server

- Create buckets
- Create groups
- Create policies
- Apply policies


Early example usage:
poetry run python dominode_extra/minioadmin.py add-department dominode-dev ppd
poetry run python dominode_extra/minioadmin.py add-user dominode-dev ppd user1 12345678

"""

import json
import shlex
import subprocess
import tempfile
import typing
from contextlib import contextmanager
from pathlib import Path
from os import fdopen

import typer
from enum import Enum
from minio import Minio

app = typer.Typer()

SUCCESS = "success"
DEFAULT_CONFIG_DIR = Path('~/.mc').expanduser()


class DepartmentName(Enum):
    PPD = 'ppd'
    LSD = 'lsd'


class DomiNodeDepartment:
    name: str
    _policy_version: str = '2012-10-17'

    def __init__(self, name: DepartmentName):
        self.name = name.value

    @property
    def staging_bucket(self) -> str:
        return f'{self.name}_staging'

    @property
    def production_bucket(self) -> str:
        return f'{self.name}_public'

    @property
    def regular_users_group(self) -> str:
        return f'{self.name}_user'

    @property
    def editors_group(self) -> str:
        return f'{self.name}_editor'

    @property
    def dominode_staging_root_dir(self) -> str:
        return f'dominode_staging/{self.name}'

    @property
    def staging_bucket_policy(self) -> typing.Dict:
        return {
            'Version': self._policy_version,
            'Statement': [
                {
                    'Sid': '',
                    'Action': [
                        's3:*'
                    ],
                    'Effect': 'Allow',
                    'Resource': [
                        f'arn:aws:s3:::{self.staging_bucket}/*'
                    ]
                }
            ]
        }

    @property
    def dominode_staging_bucket_policy(self) -> typing.Dict:
        return {
            'Version': self._policy_version,
            'Statement': [
                {
                    'Sid': '',
                    'Action': [
                        's3:*'
                    ],
                    'Effect': 'Allow',
                    'Resource': [
                        f'arn:aws:s3:::{self.dominode_staging_root_dir}/*'
                    ]
                }
            ]
        }

    @property
    def dominode_production_bucket_policy_regular_user(self) -> typing.Dict:
        return {
            'Version': self._policy_version,
            'Statement': [
                {
                    'Sid': '',
                    'Action': [
                        's3:GetBucketLocation',
                        's3:GetObject'
                    ],
                    'Effect': 'Allow',
                    'Resource': [
                        f'arn:aws:s3:::{self.dominode_staging_root_dir}/*'
                    ]
                }
            ]
        }

    @property
    def dominode_production_bucket_policy_editor_user(self) -> typing.Dict:
        return {
            'Version': self._policy_version,
            'Statement': [
                {
                    'Sid': '',
                    'Action': [
                        's3:GetBucketLocation',
                        's3:GetObject',
                        # TODO: add more actions
                        # - creating directories
                        # - copying objects from owned buckets
                        # - deleting objects objects
                        # - etc
                    ],
                    'Effect': 'Allow',
                    'Resource': [
                        f'arn:aws:s3:::{self.dominode_staging_root_dir}/*'
                    ]
                }
            ]
        }


@app.command()
def add_user(
        endpoint_alias: str,
        department_name: DepartmentName,
        access_key: str,
        secret_key: str,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    create_user(
        endpoint_alias,
        access_key,
        secret_key,
        minio_client_config_dir=minio_client_config_dir
    )
    department = DomiNodeDepartment(department_name)
    addition_result = execute_admin_command(
        endpoint_alias,
        'group add', f'{department.name} {access_key}',
        minio_client_config_dir=minio_client_config_dir
    )
    return addition_result[0].get('status') == SUCCESS



@app.command()
def add_department(
        endpoint_alias: str,
        name: DepartmentName,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    """Add a new department

    This includes:

    -  Adding department staging bucket
    -  Adding department groups

    """

    department = DomiNodeDepartment(name)

    # create groups
    # assign policies
    # create buckets/dirs
    create_group(
        endpoint_alias, department.regular_users_group, minio_client_config_dir)
    add_policy(
        endpoint_alias,
        f'{department.name}_staging_bucket_policy',
        department.dominode_staging_bucket_policy,
        department.regular_users_group,
        minio_client_config_dir
    )
    # set_policy()
    create_group(
        endpoint_alias, department.editors_group, minio_client_config_dir)


@app.command()
def remove_department(
        endpoint_alias: str,
        name: DepartmentName,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    department = DomiNodeDepartment(name)
    remove_group(endpoint_alias, department.editors_group, DEFAULT_CONFIG_DIR)
    remove_group(
        endpoint_alias, department.regular_users_group, DEFAULT_CONFIG_DIR)


def add_policy(
        endpoint_alias: str,
        name: str,
        policy: typing.Dict,
        group: str,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    existing_policies = execute_admin_command(endpoint_alias, 'policy list')
    for item in existing_policies:
        if item.get('policy') == name:
            break  # policy already exists
    else:
        os_file_handler, pathname = tempfile.mkstemp(text=True)
        with fdopen(os_file_handler, mode='w') as fh:
            json.dump(policy, fh)
        creation_result = execute_admin_command(
            endpoint_alias,
            'policy add',
            f'{name} {pathname}',
            minio_client_config_dir=minio_client_config_dir
        )
        Path(pathname).unlink(missing_ok=True)


@app.command()
def bootstrap_minio_server(
        endpoint_alias: str,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    parent_groups = [
        'dominode_user',
        'editor',
    ]
    for department in DepartmentName:
        add_department(endpoint_alias, department, minio_client_config_dir)


def create_group(
        endpoint_alias: str,
        group: str,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
) -> typing.Optional[str]:
    existing_groups = execute_admin_command(
        endpoint_alias,
        'group list',
        minio_client_config_dir=minio_client_config_dir
    )
    for existing in existing_groups:
        if existing.get('name') == group:
            result = group
            break
    else:
        # minio does not allow creating empty groups so we need a user first
        with get_temp_user(endpoint_alias, minio_client_config_dir) as user:
            temp_access_key = user[0]
            creation_result = execute_admin_command(
                endpoint_alias,
                'group add',
                f'{group} {temp_access_key}',
                minio_client_config_dir=minio_client_config_dir
            )
            relevant_result = creation_result[0]
            if relevant_result.get('status') == SUCCESS:
                result = group
            else:
                result = None
    return result


def remove_group(
        endpoint_alias: str,
        group: str,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    removal_result = execute_admin_command(
        endpoint_alias, 'group remove', group, minio_client_config_dir)
    return removal_result[0].get('status') == SUCCESS


def create_temp_user(
        endpoint_alias: str,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
) -> typing.Optional[typing.Tuple[str, str]]:
    access_key = 'tempuser'
    secret_key = '12345678'
    created = create_user(
        endpoint_alias,
        access_key,
        secret_key,
        force=True,
        minio_client_config_dir=minio_client_config_dir
    )
    if created:
        result = access_key, secret_key
    else:
        result = None
    return result


@contextmanager
def get_temp_user(
        endpoint_alias: str,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    user_creds = create_temp_user(endpoint_alias, minio_client_config_dir)
    if user_creds is not None:
        access_key, secret_key = user_creds
        try:
            yield user_creds
        finally:
            execute_admin_command(
                endpoint_alias,
                'user remove',
                access_key,
                minio_client_config_dir=minio_client_config_dir
            )


def create_user(
        endpoint_alias: str,
        access_key: str,
        secret_key: str,
        force: bool = False,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
) -> bool:
    # minio allows overwriting users with the same access_key, so we check if
    # user exists first
    existing_users = execute_admin_command(
        endpoint_alias,
        'user list',
        minio_client_config_dir=minio_client_config_dir
    )
    if len(secret_key) < 8:
        raise RuntimeError(
            'Please choose a secret key with 8 or more characters')
    for existing in existing_users:
        if existing.get('accessKey') == access_key:
            user_already_exists = True
            break
    else:
        user_already_exists = False
    if not user_already_exists or (user_already_exists and force):
        creation_result = execute_admin_command(
            endpoint_alias,
            'user add',
            f'{access_key} {secret_key}',
            minio_client_config_dir=minio_client_config_dir
        )
        result = creation_result[0].get('status') == SUCCESS
    elif user_already_exists:  # TODO: should log that user was not recreated
        result = True
    else:
        result = False
    return result


def get_client(
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool = False
) -> Minio:
    return Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )


def execute_admin_command(
        endpoint_alias: str,
        command: str,
        arguments: typing.Optional[str] = None,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
) -> typing.List:
    """Uses the ``mc`` binary to perform admin tasks on minIO servers"""
    full_command = (
        f'mc admin {command} {endpoint_alias} {arguments or ""} --json')
    full_command = full_command + f' --config-dir {minio_client_config_dir}'
    parsed_command = shlex.split(full_command)
    completed = subprocess.run(
        parsed_command,
        capture_output=True
    )
    try:
        completed.check_returncode()
    except subprocess.CalledProcessError:
        typer.echo(completed.stdout)
        raise
    result = [json.loads(line) for line in completed.stdout.splitlines()]
    return result


if __name__ == '__main__':
    app()