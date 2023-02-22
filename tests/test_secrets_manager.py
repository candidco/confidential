import pytest
import os

from confidential import SecretsManager
from confidential.exceptions import DecryptFromAWSError


def test_happy_path(secrets_file):
    with secrets_file(dan="cool") as f:
        secrets = SecretsManager(f, region_name="us-west-1")

    # Check top level decoding
    assert secrets["keep_it_secret"] == "keep_it_safe"
    assert secrets["foo"] == "bar"

    # Check nested decoding
    assert secrets["some_nested_key"]["some_int"] == 123
    assert secrets["some_nested_key"]["some_str"] == "ABC"
    assert secrets["some_nested_key"]["some_enc_str"] == "some_enc_value"

    # Check nested object decoding
    assert secrets["nested_object"] == {"foo": "bar"}

    # Check SSM parameter decoding
    assert secrets["parameter_key"] == "ssm_parameter_value"
    assert secrets["nested_object_parameter"] == {"ping": "pong"}
    assert secrets["nested_parameter_key"] == {"temp_c": 3, "snow_fall_cm": 20, "some_parameter": "cold"}


def test_secrets_exported_to_env_vars(secrets_file):
    with secrets_file(foo="bar", ping="pong") as f:
        secrets = SecretsManager(f, region_name="us-west-1", export_env_variables=True)

    assert os.environ.get("FOO") == "bar"
    assert secrets["foo"] == os.environ.get("FOO")

    assert os.environ.get("PING") == "pong"
    assert secrets["ping"] == os.environ.get("PING")

    assert os.environ.get("blah") == None
    assert secrets["blah"] == os.environ.get("BLAH")


@pytest.mark.parametrize(
    "secret_value_response,error_msg",
    [
        (
            {"FakeKey": "FakeValue"},
            "Error decrypting SecretId=keep_it_secret. `SecretString` not found in AWS response. Does the IAM user have correct permissions?",
        ),
        (
            {"SecretString": None},
            "Error decrypting SecretId=keep_it_secret. `SecretString` was `None`. Does the IAM user have correct permissions?",
        ),
    ],
)
def test_missing_or_none_secret_string_raises_decrypt_from_aws_error(secret_value_response, error_msg, mocker, secrets_file):
    mock_boto = mocker.patch("confidential.secrets_manager.boto3.session.Session")
    client_mock = mocker.Mock()
    client_mock.client.return_value.get_secret_value.return_value = secret_value_response
    mock_boto.return_value = client_mock

    with pytest.raises(DecryptFromAWSError) as exc_info:
        with secrets_file() as f:
            SecretsManager(f, region_name="us-west-1")

    assert str(exc_info.value) == error_msg


@pytest.mark.parametrize(
    "secret_value_response,error_msg",
    [
        (
            {"FakeKey": "FakeValue"},
            "Error decrypting Name=parameter_key. `Parameter.Value` not found in AWS response. Does the IAM user have correct permissions?",
        ),
        (
            {"Parameter": {"FakeKey": "FakeValue"}},
            "Error decrypting Name=parameter_key. `Parameter.Value` not found in AWS response. Does the IAM user have correct permissions?",
        ),
        (
            {"Parameter": {"Value": None}},
            "Error decrypting Name=parameter_key. `Parameter.Value` was `None`. Does the IAM user have correct permissions?",
        ),
    ],
)
def test_missing_or_none_parameter_value_raises_decrypt_from_aws_error(secret_value_response, error_msg, mocker, ssm_params_file):
    mock_boto = mocker.patch("confidential.secrets_manager.boto3.session.Session")
    client_mock = mocker.Mock()
    client_mock.client.return_value.get_parameter.return_value = secret_value_response
    mock_boto.return_value = client_mock

    with pytest.raises(DecryptFromAWSError) as exc_info:
        with ssm_params_file() as f:
            SecretsManager(f, region_name="us-west-1")

    assert str(exc_info.value) == error_msg
