from botocore.exceptions import ClientError
from confidential.exceptions import DecryptFromAWSError


class SecretsManagerDecrypter:
    def __init__(self, session=None, region_name=None):
        self.SERVICE_NAME = "secretsmanager"
        self.SECRET_PREFIX = "secret:"
        self.client = session.client(service_name=self.SERVICE_NAME, region_name=region_name)

    def decrypt_secret_from_aws(self, secret) -> str:
        """
        Decrypts a secret from AWS Secret Manager
        """
        secret_id = secret[len(self.SECRET_PREFIX) :]
        try:
            get_secret_value_response = self.client.get_secret_value(SecretId=secret_id)
        except ClientError as e:
            raise DecryptFromAWSError(
                f"Error decrypting {secret_id}. {e.response['Error']['Code']}: {e.response['Error']['Message']}"
            )
        else:
            try:
                secret_string = get_secret_value_response["SecretString"]
                if secret_string is None:
                    raise DecryptFromAWSError(
                        f"Error decrypting SecretId={secret_id}. `SecretString` was `None`. Does the IAM user have correct permissions?"
                    )
            except KeyError as e:
                raise DecryptFromAWSError(
                    f"Error decrypting SecretId={secret_id}. `SecretString` not found in AWS response. Does the IAM user have correct permissions?"
                )
            else:
                return secret_string
