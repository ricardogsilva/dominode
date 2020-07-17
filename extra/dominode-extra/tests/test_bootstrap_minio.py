import typing

import pytest
from minio import Minio


@pytest.mark.parametrize('access_key, expected_num_buckets', [
    pytest.param('ppd_user1', 2)
])
def test_regular_user_has_access_to_buckets(
        minio_server_info,
        bootstrapped_minio_server,
        minio_users_credentials,
        access_key,
        expected_num_buckets
):
    minio_client = _get_minio_client(access_key, minio_users_credentials, minio_server_info['port'])
    buckets = minio_client.list_buckets()
    print(f'buckets: {buckets}')
    assert len(buckets) == expected_num_buckets


def _get_minio_client(
        access_key: str,
        minio_users_credentials: typing.Dict,
        port: int,
):
    secret_key = minio_users_credentials[access_key][0]
    endpoint = f'localhost:{port}'
    return Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )
