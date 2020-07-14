import pytest


def test_minio_server_comes_up(minio_client):
    buckets = minio_client.list_buckets()
    print(f'buckets: {buckets}')
    assert len(buckets) > 0