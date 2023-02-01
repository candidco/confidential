from botocore.exceptions import ClientError
from confidential.exceptions import PermissionError

class SecretsManagerDecrypter:
    def __init__(self, session=None, region_name=None):
        self.SERVICE_NAME = "secretsmanager"
        self.SECRET_PREFIX = "secret:"
        self.client = session.client(service_name=self.SERVICE_NAME, region_name=region_name)
    
    def decrypt_secret_from_aws(self, secret) -> str:
        """
        Decrypts a secret from AWS Secret Manager
        """
        secret_id = secret[len(self.SECRET_PREFIX):]
        try:
            get_secret_value_response = self.client.get_secret_value(SecretId=secret_id)

        except ClientError as e:
            if e.response["Error"]["Code"] == "DecryptionFailureException":
                raise Exception("can't decrypt the protected secret text using the provided KMS key.") from e

            elif e.response["Error"]["Code"] == "InternalServiceErrorException":
                raise Exception("An error occurred on the server side.") from e

            elif e.response["Error"]["Code"] == "InvalidParameterException":
                raise Exception("You provided an invalid value for a parameter.") from e

            elif e.response["Error"]["Code"] == "InvalidRequestException":
                raise Exception("Invalid parameter value for the current state of the resource.") from e

            elif e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise Exception("We can't find the resource that you asked for.") from e

        else:
            if "SecretString" not in get_secret_value_response or get_secret_value_response["SecretString"] is None:
                raise PermissionError(
                    "`SecretString` not found in AWS response, does the IAM user have correct permissions?"
                )

            return get_secret_value_response["SecretString"]
