import json
import logging
import os
from botocore.exceptions import ClientError

from confidential.exceptions import PermissionError
from confidential.utils import merge

log = logging.getLogger(__name__)


class ParameterStore:
    def __init__(self, secrets=None, secrets_defaults=None, region_name=None, session=None):
        self.session = session
        self.client = session.client(service_name="ssm", region_name=region_name)

        secrets_defaults = self.parse_secrets(secrets_defaults) if secrets_defaults else {}
        secrets = self.parse_secrets(secrets) if secrets else {}

        self.secrets = merge(secrets_defaults, secrets)

    def __getitem__(self, key):
        """
        Allows us to access items directly.
        """
        value = self.secrets.get(key)
        if value is None:
            raise Exception(f"Value for '{key}' was not found in the secrets file", self.secrets)
        return value

    def decrypt_secret_from_aws(self, secret_name) -> str:
        """
        Decrypts a secret from AWS Parameter Store.
        """
        try:
            get_secret_value_response = self.client.get_parameter(Name=secret_name, WithDecryption=True)

        except ClientError as e:
            if e.response["Error"]["Code"] == "DecryptionFailureException":
                raise Exception("can't decrypt the protected secret text using the provided KMS key.") from e

            elif e.response["Error"]["Code"] == "InternalServerError":
                raise Exception("An error occurred on the server side.") from e

            elif e.response["Error"]["Code"] == "ParameterNotFound":
                raise Exception("You provided an invalid value for a parameter.") from e

            elif e.response["Error"]["Code"] == "ParameterVersionNotFound":
                raise Exception("Invalid parameter value for the current state of the resource.") from e

            elif e.response["Error"]["Code"] == "InvalidKeyId":
                raise Exception("We can't find the resource that you asked for.") from e
            
            elif e.response["Error"]["Code"] == "UnrecognizedClientException":
                raise Exception("The security token included in the request is invalid.") from e

            else:
                raise e
        else:
            if "Parameter" not in get_secret_value_response or get_secret_value_response["Parameter"]["Value"] is None:
                raise PermissionError(
                    "`Value` not found in AWS response, does the IAM user have correct permissions?"
                )
            return get_secret_value_response["Parameter"]["Value"]

    def traverse_and_decrypt(self, config):
        """
        Recursively walks the dictionary of values, and decrypts values if necessary
        """
        for key, value in config.items():
            if isinstance(value, dict):
                self.traverse_and_decrypt(value)
            else:
                config[key] = self.decrypt_string(value)

    def decrypt_string(self, value) -> str:
        """
        Attempts to decrypt an encrypted string.
        """

        if not (isinstance(value, str) and value.startswith("ssm:")):
            return value

        decrypted_string = self.decrypt_secret_from_aws(value[4:])

        # Check if the payload is serialized JSON
        try:
            result = json.loads(decrypted_string)
        except json.decoder.JSONDecodeError:
            result = decrypted_string
        return result

    def parse_secrets(self, secrets) -> dict:
        """
        Parses a JSON dictionary and returns a decrypted JSON dictionary
        """
        secrets_dict = secrets
        self.traverse_and_decrypt(secrets_dict)

        return secrets_dict
