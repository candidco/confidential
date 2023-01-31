import boto3
import click
import pprint
import json
import os

from confidential.secrets_manager import SecretsManager
from confidential.parameter_store import ParameterStore
from confidential.utils import merge

class ConfigsManager:
    def __init__(self, secrets_file=None, secrets_file_default=None, region_name=None, profile_name=None):
        session = boto3.session.Session(profile_name=profile_name)

        self.session = session

        secrets_defaults = self.import_secrets_file(secrets_file_default) if secrets_file_default else {}
        secrets = self.import_secrets_file(secrets_file) if secrets_file else {}

        secrets_manager = SecretsManager(secrets=secrets, secrets_defaults=secrets_defaults, region_name=region_name, session=session)
        decrypted_secrets = secrets_manager.secrets

        parameter_store = ParameterStore(secrets=decrypted_secrets, region_name=region_name, session=session)
        decrypted_parameters = parameter_store.secrets

        self.secrets = merge(decrypted_secrets, decrypted_parameters)

    @staticmethod
    def import_secrets_file(path_to_file) -> dict:
        """
        Imports a JSON file and returns a Python dictionary
        """
        if not os.path.exists(path_to_file):
            raise Exception(f"Specified file '{path_to_file}' does not exist")

        with open(path_to_file) as file_object:
            return json.load(file_object)

@click.command()
@click.argument("secrets_file", type=click.Path(exists=True))
@click.option("--default_secrets_file", default=None, help="A default secrets file that will be overridden")
@click.option("-p", "--profile", default=None, help="AWS Profile")
@click.option("--aws_region", help="AWS Region", default="us-east-1")
@click.option("--output-json", help="Return secrets as JSON", is_flag=True)
def decrypt_secret(secrets_file, default_secrets_file, profile, aws_region, output_json):
    pp = pprint.PrettyPrinter(indent=4)
    configs_manager = ConfigsManager(
        secrets_file=secrets_file,
        secrets_file_default=default_secrets_file,
        region_name=aws_region,
        profile_name=profile,
    )
    if output_json is True:
        print(json.dumps(configs_manager.secrets))
    else:
        pp.pprint(configs_manager.secrets)


if __name__ == "__main__":
    decrypt_secret()
