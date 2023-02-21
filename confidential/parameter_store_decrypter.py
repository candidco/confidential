from botocore.exceptions import ClientError
from confidential.exceptions import DecryptFromAWSError


class ParameterStoreDecrypter:
    def __init__(self, session=None, region_name=None):
        self.SERVICE_NAME = "ssm"
        self.SECRET_PREFIX = "ssm:"
        self.client = session.client(service_name=self.SERVICE_NAME, region_name=region_name)

    def decrypt_secret_from_aws(self, secret) -> str:
        """
        Decrypts a parameter from AWS Parameter Store.
        """
        name = secret[len(self.SECRET_PREFIX) :]
        try:
            get_parameter_response = self.client.get_parameter(Name=name, WithDecryption=True)
        except ClientError as e:
            raise DecryptFromAWSError(
                f"Error decrypting Name={name}. {e.response['Error']['Code']}: {e.response['Error']['Message']}"
            )
        else:
            try:
                parameter_value = get_parameter_response["Parameter"]["Value"]
                if parameter_value is None:
                    raise DecryptFromAWSError(
                        f"Error decrypting Name={name}. `Parameter.Value` was `None`. Does the IAM user have correct permissions?"
                    )
            except KeyError as e:
                raise DecryptFromAWSError(
                    f"Error decrypting Name={name}. `Parameter.Value` not found in AWS response. Does the IAM user have correct permissions?"
                )
            else:
                return parameter_value
