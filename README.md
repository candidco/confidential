![confidential](https://user-images.githubusercontent.com/1169974/64377143-c7f36680-cff7-11e9-9616-e6c4b8b897b2.png)

# Confidential

## Installation

```
pip install confidential
```

## How does it work?

Confidential manages secrets for your project, using AWS Secrets Manager.

First, create a secrets file, `my_secrets.json`
```json
{
  "database": "secret:database_details",
  "environment": "production",
  "debug_mode": false
}
```  

Mark a value as needing decryption by prepending `secret` to it, like `database` above.
 
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

## Can I use it in my Python projects?

Of-course!

`settings.py`
```python
from confidential import SecretManager


secrets = SecretManager("production.json", "defaults.json")

DATABASES = {
    'default': secrets["database"]
}
```
