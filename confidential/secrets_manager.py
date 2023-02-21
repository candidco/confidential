import boto3
import click
import json
import logging
import os
import pprint

from confidential.secrets_manager_decrypter import SecretsManagerDecrypter
from confidential.parameter_store_decrypter import ParameterStoreDecrypter
from confidential.exceptions import DecryptFromAWSError
from confidential.utils import merge

log = logging.getLogger(__name__)


class SecretsManager:
    def __init__(self, secrets_file=None, secrets_file_default=None, region_name=None, profile_name=None, export_env_variables=False):
        session = boto3.session.Session(profile_name=profile_name)

        self.session = session
        secrets_manager_decrypter = SecretsManagerDecrypter(session=session, region_name=region_name)
        parameter_store_decrypter = ParameterStoreDecrypter(session=session, region_name=region_name)

        self.decrypters = [secrets_manager_decrypter, parameter_store_decrypter]

        secrets_defaults = self.parse_secrets_file(secrets_file_default) if secrets_file_default else {}
        secrets = self.parse_secrets_file(secrets_file) if secrets_file else {}

        self.secrets = merge(secrets_defaults, secrets)

        if export_env_variables:
            self.export_env_variables(self.secrets)

    def __getitem__(self, key):
        """
        Allows us to do <SecretsManager>["foo"] instead of <SecretsManager>.secrets.get("foo")
        """
        value = self.secrets.get(key)
        if value is None:
            log.warning(f"Value for '{key}' was not found in the secrets file. Returning 'None'.")
        return value

    @staticmethod
    def import_secrets_file(path_to_file) -> dict:
        """
        Imports a JSON file and returns a Python dictionary
        """
        if not os.path.exists(path_to_file):
            raise Exception(f"Specified file '{path_to_file}' does not exist")

        with open(path_to_file) as file_object:
            return json.load(file_object)

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

        supported_decrypter = self.find_supported_decrypter(value)
        if not (supported_decrypter):
            return value

        decrypted_string = supported_decrypter.decrypt_secret_from_aws(value)

        # Check if the payload is serialized JSON
        try:
            result = json.loads(decrypted_string)
        except json.decoder.JSONDecodeError:
            result = decrypted_string
        return result

    def find_supported_decrypter(self, value):
        if isinstance(value, str):
            supported = list(filter(lambda decrypter: value.startswith(decrypter.SECRET_PREFIX), self.decrypters))
            return next(iter(supported), None)
        else:
            return None

    def parse_secrets_file(self, path_to_file) -> dict:
        """
        Imports and parses a JSON file and returns a decrypted JSON dictionary
        """
        config = self.import_secrets_file(path_to_file)

        self.traverse_and_decrypt(config)

        return config

    def export_env_variables(self, secrets):
        for key in secrets:
            uppercase_key = key.upper()
            os.environ[uppercase_key] = str(secrets[key])


@click.command()
@click.argument("secrets_file", type=click.Path(exists=True))
@click.option("--default_secrets_file", default=None, help="A default secrets file that will be overridden")
@click.option("-p", "--profile", default=None, help="AWS Profile")
@click.option("--aws_region", help="AWS Region", default="us-east-1")
@click.option("--output-json", help="Return secrets as JSON", is_flag=True)
def decrypt_secret(secrets_file, default_secrets_file, profile, aws_region, output_json):
    pp = pprint.PrettyPrinter(indent=4)
    secrets_manager = SecretsManager(
        secrets_file=secrets_file,
        secrets_file_default=default_secrets_file,
        region_name=aws_region,
        profile_name=profile,
    )
    if output_json is True:
        print(json.dumps(secrets_manager.secrets))
    else:
        pp.pprint(secrets_manager.secrets)


if __name__ == "__main__":
    decrypt_secret()
