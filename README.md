# 🤫 Confidential

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

## Usage in Python projects

`settings.py`
```
from confidential import SecretManager


SECRETS_FILE = os.environ.get("SECRETS_FILE", ".secrets/defaults.json")
secrets = SecretManager(SECRETS_FILE)

DATABASES = {
    'default': secrets["database"]
}
```