from botocore.exceptions import ClientError
from confidential.exceptions import PermissionError


class ParameterStoreDecrypter:
    def __init__(self, session=None, region_name=None):
        self.SERVICE_NAME = "ssm"
        self.SECRET_PREFIX = "ssm:"
        self.client = session.client(service_name=self.SERVICE_NAME, region_name=region_name)

    def decrypt_secret_from_aws(self, secret) -> str:
        """
        Decrypts a secret from AWS Parameter Store.
        """
        secret_id = secret[len(self.SECRET_PREFIX):]
        try:
            get_secret_value_response = self.client.get_parameter(Name=secret_id, WithDecryption=True)

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
                raise PermissionError("`Value` not found in AWS response, does the IAM user have correct permissions?")
            return get_secret_value_response["Parameter"]["Value"]
