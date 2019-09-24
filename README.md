![confidential](https://user-images.githubusercontent.com/1169974/64377143-c7f36680-cff7-11e9-9616-e6c4b8b897b2.png)

![badge](https://action-badges.now.sh/candidco/confidential?action=pytest)

## Installation

```
pip install confidential
```

## How does it work?

Confidential manages secrets for your project, using AWS Secrets Manager.

First, store a secret in AWS Secrets Manager. Then, create a secrets file, say `my_secrets.json`. A value will be decrypted if the word `secret` precedes it, like the `database` value below:

```json
{
  "database": "secret:database_details",
  "environment": "production",
  "debug_mode": false
}
```  
 
You can decrypt this file using the CLI:

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


secrets = SecretManager("production.json", "defaults.json", region="us-east-1")

DATABASES = {
    'default': secrets["database"]
}
```

# Testing

First, install all dependencies:

```bash
poetry install
```

Then run the tests
```bash
poetry run pytest
```
