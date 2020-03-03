import json
import tempfile
from contextlib import contextmanager

import boto3
import pytest
from moto import mock_secretsmanager


@pytest.yield_fixture(autouse=True)
def mock_secrets_manager():
    """
    Starts moto at the beginning of tests, and closes it at the end of the session
    """
    mock = mock_secretsmanager()
    mock.start()
    yield
    mock.stop()


@pytest.fixture()
def store_secret():
    """
    Stores a secret in SecretsManager (mocked)
    """

    def wrapped(key, value):
        sm = boto3.client("secretsmanager", region_name="us-west-1")
        sm.create_secret(Name=key, SecretString=value)

    return wrapped


@pytest.fixture
def secrets(store_secret):
    store_secret("keep_it_secret", "keep_it_safe")
    store_secret("nested_object", '{"foo": "bar"}')
    store_secret("some_enc_str", "some_enc_value")

    def wrapped(**overrides):
        d = {
            "foo": "bar",
            "keep_it_secret": "secret:keep_it_secret",
            "some_nested_key": {"some_int": 123, "some_str": "ABC", "some_enc_str": "secret:some_enc_str"},
            "nested_object": "secret:nested_object",
        }
        d.update(overrides)
        return d

    return wrapped


@pytest.fixture
def secrets_file(secrets):
    @contextmanager
    def wrapped(**overrides):
        tf = tempfile.NamedTemporaryFile()
        tf.write(json.dumps(secrets(**overrides)).encode("utf8"))
        tf.seek(0)
        yield tf.name
        tf.close()

    return wrapped
