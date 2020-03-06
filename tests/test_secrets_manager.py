import pytest

from confidential import SecretsManager
from confidential.exceptions import PermissionError


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


@pytest.mark.parametrize("secret_value_response", [{"FakeKey": "FakeValue"}, {"SecretString": None}])
def test_missing_secret_string_raises_permission_error(secret_value_response, mocker, secrets_file):
    mock_boto = mocker.patch("confidential.secrets_manager.boto3.session.Session")
    client_mock = mocker.Mock()
    client_mock.client.return_value.get_secret_value.return_value = secret_value_response
    mock_boto.return_value = client_mock

    with pytest.raises(PermissionError) as exc_info:
        with secrets_file() as f:
            SecretsManager(f, region_name="us-west-1")

    assert (
        str(exc_info.value) == "`SecretString` not found in AWS response, does the IAM user have correct permissions?"
    )
