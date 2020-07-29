"""Extra admin commands to manage the DomiNode minIO server

This script adds some functions to perform DomiNode related tasks in a more
expedite manner than using the bare minio client `mc`.

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

from .constants import (
    DepartmentName,
    UserRole
)

_help_intro = 'Manage minIO server'

app = typer.Typer(
    short_help=_help_intro,
    help=(
        f'{_help_intro} - Be sure to install minio CLI client (mc) before '
        f'using this. Also, create a \'~/.mc/config.json\' file with the '
        f'credentials of the minIO server that you want to use. Check out the'
        f'minIO client docs at: \n\n'
        f'https://docs.min.io/docs/minio-client-quickstart-guide.html\n\n'
        f'for details on how to download mc and configure it.'
    )
)

SUCCESS = "success"
DEFAULT_CONFIG_DIR = Path('~/.mc').expanduser()


class DomiNodeDepartment:
    name: str
    endpoint_alias: str
    minio_client_config_dir: Path = DEFAULT_CONFIG_DIR
    dominode_staging_bucket: str = 'dominode-staging'
    public_bucket: str = 'public'
    _policy_version: str = '2012-10-17'

    def __init__(
            self,
            name: DepartmentName,
            endpoint_alias: str,
            minio_client_config_dir: typing.Optional[Path] = None
    ):
        self.name = name.value
        self.endpoint_alias = endpoint_alias
        if minio_client_config_dir is not None:
            self.minio_client_config_dir = minio_client_config_dir

    @property
    def staging_bucket(self) -> str:
        return f'{self.name}-staging'

    @property
    def dominode_staging_root_dir(self) -> str:
        return f'{self.dominode_staging_bucket}/{self.name}/'

    @property
    def production_bucket_root_dir(self) -> str:
        return f'{self.public_bucket}/{self.name}/'

    @property
    def regular_users_group(self) -> str:
        return f'{self.name}-user'

    @property
    def editors_group(self) -> str:
        return f'{self.name}-editor'

    @property
    def regular_user_policy(self) -> typing.Tuple[str, typing.Dict]:
        return (
            f'{self.name}-regular-user-group-policy',
            {
                'Version': self._policy_version,
                'Statement': [
                    {
                        'Sid': f'{self.name}-regular-user-deny-bucket-delete',
                        'Action': [
                            's3:DeleteBucket',
                        ],
                        'Effect': 'Deny',
                        'Resource': [
                            f'arn:aws:s3:::{self.dominode_staging_bucket}',
                            f'arn:aws:s3:::{self.staging_bucket}',
                        ]
                    },
                    {
                        'Sid': f'{self.name}-regular-user-full-access',
                        'Action': [
                            's3:*'
                        ],
                        'Effect': 'Allow',
                        'Resource': [
                            f'arn:aws:s3:::{self.dominode_staging_root_dir}*',
                            f'arn:aws:s3:::{self.staging_bucket}/*',
                        ]
                    },
                    {
                        'Sid': f'{self.name}-regular-user-read-only',
                        'Action': [
                            's3:GetBucketLocation',
                            's3:ListBucket',
                            's3:GetObject',
                        ],
                        'Effect': 'Allow',
                        'Resource': [
                            f'arn:aws:s3:::{self.dominode_staging_bucket}/*',
                            f'arn:aws:s3:::{self.public_bucket}/*'
                        ]
                    },
                ]
            }
        )

    @property
    def editor_user_policy(self) -> typing.Tuple[str, typing.Dict]:
        return (
            f'{self.name}-editor-group-policy',
            {
                'Version': self._policy_version,
                'Statement': [
                    {
                        'Sid': f'{self.name}-editor-user-deny-bucket-delete',
                        'Action': [
                            's3:DeleteBucket',
                        ],
                        'Effect': 'Deny',
                        'Resource': [
                            f'arn:aws:s3:::{self.dominode_staging_bucket}',
                            f'arn:aws:s3:::{self.staging_bucket}',
                        ]
                    },
                    {
                        'Sid': f'{self.name}-editor-full-access',
                        'Action': [
                            's3:*'
                        ],
                        'Effect': 'Allow',
                        'Resource': [
                            f'arn:aws:s3:::{self.staging_bucket}/*',
                            f'arn:aws:s3:::{self.dominode_staging_root_dir}*',
                            f'arn:aws:s3:::{self.production_bucket_root_dir}*',
                        ]
                    },
                    {
                        'Sid': f'{self.name}-editor-read-only',
                        'Action': [
                            's3:GetBucketLocation',
                            's3:ListBucket',
                            's3:GetObject',
                        ],
                        'Effect': 'Allow',
                        'Resource': [
                            f'arn:aws:s3:::{self.dominode_staging_bucket}/*',
                            f'arn:aws:s3:::{self.public_bucket}/*'
                        ]
                    },
                ]
            }
        )

    def create_groups(self):
        create_group(
            self.endpoint_alias,
            self.regular_users_group,
            self.minio_client_config_dir
        )
        create_group(
            self.endpoint_alias,
            self.editors_group,
            self.minio_client_config_dir
        )

    def create_buckets(self):
        extra = '--ignore-existing'
        self._execute_command('mb', f'{self.staging_bucket} {extra}')
        self._execute_command('mb', f'{self.dominode_staging_root_dir} {extra}')
        self._execute_command(
            'mb', f'{self.production_bucket_root_dir} {extra}')

    def create_policies(self):
        self.add_policy(*self.regular_user_policy)
        self.add_policy(*self.editor_user_policy)

    def add_policy(self, name: str, policy: typing.Dict):
        """Add policy to the server"""
        existing_policies = self._execute_admin_command('policy list')
        for item in existing_policies:
            if item.get('policy') == name:
                break  # policy already exists
        else:
            os_file_handler, pathname = tempfile.mkstemp(text=True)
            with fdopen(os_file_handler, mode='w') as fh:
                json.dump(policy, fh)
            self._execute_admin_command(
                'policy add',
                f'{name} {pathname}',
            )
            Path(pathname).unlink(missing_ok=True)

    def set_policies(self):
        self.set_policy(self.regular_user_policy[0], self.regular_users_group)
        self.set_policy(self.editor_user_policy[0], self.editors_group)
        self._set_public_policy()

    def _set_public_policy(self):
        self._execute_command(
            'policy set download',
            f'{self.production_bucket_root_dir}*'
        )

    def set_policy(
            self,
            policy: str,
            group: str,
    ):
        self._execute_admin_command(
            'policy set',
            f'{policy} group={group}',
        )

    def add_user(
            self,
            access_key: str,
            secret_key: str,
            role: typing.Optional[UserRole] = UserRole.REGULAR_DEPARTMENT_USER
    ):
        create_user(
            self.endpoint_alias,
            access_key,
            secret_key,
            minio_client_config_dir=self.minio_client_config_dir
        )
        group = {
            UserRole.REGULAR_DEPARTMENT_USER: self.regular_users_group,
            UserRole.EDITOR: self.editors_group,
        }[role]
        addition_result = self._execute_admin_command(
            'group add', f'{group} {access_key}',)
        return addition_result[0].get('status') == SUCCESS

    def _execute_command(
            self,
            command: str,
            arguments: typing.Optional[str] = None,
    ):
        return execute_command(
            self.endpoint_alias,
            command,
            arguments,
            self.minio_client_config_dir
        )

    def _execute_admin_command(
            self,
            command: str,
            arguments: typing.Optional[str] = None,
    ):
        return execute_admin_command(
            self.endpoint_alias,
            command,
            arguments,
            self.minio_client_config_dir
        )


@app.command()
def add_department_user(
        endpoint_alias: str,
        access_key: str,
        secret_key: str,
        department_name: DepartmentName,
        role: typing.Optional[UserRole] = UserRole.REGULAR_DEPARTMENT_USER,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    """Create a user and add it to the relevant department groups

    This function shall ensure that when a new user is created it is put in the
    relevant groups and with the correct access policies

    """

    department = DomiNodeDepartment(
        department_name, endpoint_alias, minio_client_config_dir)
    return department.add_user(access_key, secret_key, role)


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

    department = DomiNodeDepartment(
        name, endpoint_alias, minio_client_config_dir)
    # typer.echo(f'department config_dir: {department.minio_client_config_dir}')
    department.create_groups()
    department.create_buckets()
    department.create_policies()
    department.set_policies()


@app.command()
def bootstrap(
        endpoint_alias: str,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    """Perform initial bootstrap of the minIO server

    This function will take care of creating the relevant buckets, groups and
    access controls for using the minIO server for DomiNode.

    """

    for member in DepartmentName:
        add_department(endpoint_alias, member, minio_client_config_dir)


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


def execute_command(
        endpoint_alias: str,
        command: str,
        arguments: typing.Optional[str] = None,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
):
    full_command = (
        f'mc --config-dir {minio_client_config_dir} --json {command} '
        f'{"/".join((endpoint_alias, arguments or ""))}'
    )
    typer.echo(full_command)
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


def execute_admin_command(
        endpoint_alias: str,
        command: str,
        arguments: typing.Optional[str] = None,
        minio_client_config_dir: typing.Optional[Path] = DEFAULT_CONFIG_DIR
) -> typing.List:
    """Uses the ``mc`` binary to perform admin tasks on minIO servers"""
    full_command = (
        f'mc --config-dir {minio_client_config_dir} --json admin {command} '
        f'{endpoint_alias} {arguments or ""}'
    )


    parsed_command = shlex.split(full_command)
    completed = subprocess.run(
        parsed_command,
        capture_output=True
    )
    try:
        completed.check_returncode()
    except subprocess.CalledProcessError:
        typer.echo(completed.stdout)
        typer.echo(completed.stderr)
        raise
    result = [json.loads(line) for line in completed.stdout.splitlines()]
    return result


if __name__ == '__main__':
    app()