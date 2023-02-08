![confidential](https://user-images.githubusercontent.com/1169974/64377143-c7f36680-cff7-11e9-9616-e6c4b8b897b2.png)

![badge](https://action-badges.now.sh/candidco/confidential?action=pytest)

## Installation

```
pip install confidential
```

## How does it work?

Confidential manages secrets for your project, using AWS Secrets Manager and SSM Parameter Store.

First, store a secret in AWS Secrets Manager. Then, create a secrets file, say `my_secrets.json`. A value will be decrypted if the word `secret` precedes it, like the `database` value below:

```json
{
  "database": "secret:database_details",
  "environment": "production",
  "debug_mode": false
}
```

Similarly, SSM Parameters can be referenced by providing a parameter key, e.g.: `"ssm:some_ssm_parameter_key"`.
 
You can decrypt this file either in Python, or directly using the CLI. Ensure [AWS CLI](https://aws.amazon.com/cli/) is set up, then run:

```bash
confidential my_secrets.json
```

which outputs the file with decrypted values
```json
{
  "database": {
    "url": "https://example.com",
    "username": "admin",
    "password": "p@55w0rd",
    "port": 5678
  },
  "environment": "production",
  "debug_mode": false
}
```

![image](https://user-images.githubusercontent.com/1169974/64388843-64286800-d00e-11e9-8fa2-7935b3d4f1ca.png)


## Can I use it in my Python projects?

Yes, simply import and instantiate `SecretsManager`, like so:

`settings.py`
```python
from confidential import SecretsManager


secrets = SecretManager(
    secrets_file=".secrets/production.json",
    secrets_file_default=".secrets/defaults.json",  # Overridable defaults you can use in common environments
    region_name="us-east-1",
)

DATABASES = {
    'default': secrets["database"]
}
```

If `export_env_variables` is set to `True`, each secret will also be exported as an environment variable, with the uppercase key as the variable name, e.g.:

```python
from confidential import SecretsManager
import os

secrets = SecretManager(
    secrets_file=".secrets/production.json",
    secrets_file_default=".secrets/defaults.json",  # Overridable defaults you can use in common environments
    region_name="us-east-1",
    export_env_variables=True,  # Optionally, export secrets as environment variables. Default is False.
)

# If the key of a secret is `api_key`, then the following is true:
assert secrets["api_key"] == os.environ.get("API_KEY")
```

Trying to access an inexisting key returns `None`. On previous versions, it would throw an exception.

# Testing

First, install all dependencies:

```bash
poetry install
```

Then run the tests
```bash
poetry run pytest
```
