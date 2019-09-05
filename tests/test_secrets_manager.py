from confidential import SecretsManager


def test_happy_path(secrets_file):
    with secrets_file(dan="cool") as f:
        secrets = SecretsManager(f, region_name="us-west-1")

    # Check that we correctly decrypt from AWS Secrets Manager
    assert secrets["keep_it_secret"] == "keep_it_safe"

    # Check that we correct import plain text
    assert secrets["foo"] == "bar"
