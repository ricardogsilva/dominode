import os
import typing
from configparser import ConfigParser
from pathlib import Path

import typer

from .constants import DepartmentName

_DEFAULT_CONFIG_PATHS = (
    Path('/etc/dominode/.dominode-bootstrapper.conf'),
    Path('~/.dominode-bootstrapper.conf').expanduser(),
    Path(__file__).resolve().parents[1] / '.dominode-bootstrapper.conf',
    os.getenv('DOMINODE_BOOTSTRAPPER_CONFIG_PATH', '/dev/null'),
)


def load_config(
        paths: typing.Optional[
            typing.Iterable[typing.Union[str, Path]]
        ] = _DEFAULT_CONFIG_PATHS
) -> ConfigParser:
    """Load configuration values

    Config is composed by looking for values in multiple places:

    - Default config values, as specified in the ``_get_default_config()``
      function

    - The following paths, if they exist:
      - /etc/dominode/.dominode-bootstrapper.conf
      - $HOME/.dominode-bootstrapper.conf
      - {current-directory}/.dominode-bootstrapper.conf
      - whatever file is specified by the DOMINODE_BOOTSTRAPPER_CONFIG_PATH
        environment variable

    - Environment variables named like `DOMINODE__{SECTION}__{KEY}`

    """

    config = _get_default_config()
    read_from = config.read(paths)
    typer.echo(f'Read config from {", ".join(read_from)}')
    for section, section_options in get_config_from_env().items():
        for key, value in section_options.items():
            try:
                config[section][key] = value
            except KeyError:
                config[section] = {key: value}
    return config


def get_config_from_env() -> typing.Dict[str, typing.Dict[str, str]]:
    result = {}
    for key, value in os.environ.items():
        if key.startswith('DOMINODE__DEPARTMENT__'):
            try:
                department, config_key = key.split('__')[2:]
            except ValueError:
                typer.echo(f'Could not read variable {key}, ignoring...')
                continue
            section_name = f'{department.lower()}-department'
            department_section = result.setdefault(section_name, {})
            department_section[config_key.lower()] = value
        elif key.startswith('DOMINODE__DB__'):
            try:
                config_key = key.split('__')[-1]
            except ValueError:
                typer.echo(f'Could not read variable {key}, ignoring...')
                continue
            db_section = result.setdefault('db', {})
            db_section[config_key.lower()] = value
        elif key.startswith('DOMINODE__MINIO__'):
            try:
                config_key = key.split('__')[-1]
            except ValueError:
                typer.echo(f'Could not read variable {key}, ignoring...')
                continue
            minio_section = result.setdefault('minio', {})
            minio_section[config_key.lower()] = value
    return result


def _get_default_config():
    config = ConfigParser()
    for member in DepartmentName:
        section_name = f'{member.value}-department'
        config[section_name] = {}
        config[section_name]['geoserver_password'] = "dominode"
    config['db'] = {}
    config['db']['name'] = 'postgres'
    config['db']['host'] = 'localhost'
    config['db']['port'] = '5432'
    config['db']['admin_username'] = 'postgres'
    config['db']['admin_password'] = 'postgres'
    config['minio'] = {}
    config['minio']['host'] = 'localhost'
    config['minio']['port'] = '9000'
    config['minio']['protocol'] = 'https'
    config['minio']['admin_access_key'] = 'admin'
    config['minio']['admin_secret_key'] = 'admin'
    return config


def get_departments(config: ConfigParser) -> typing.List[str]:
    separator = '-'
    result = []
    for section in config.sections():
        if section.endswith(f'{separator}department'):
            result.append(section.partition(separator)[0])
    return result