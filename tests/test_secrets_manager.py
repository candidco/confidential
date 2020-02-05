from confidential import SecretsManager


def test_happy_path(secrets_file):
    with secrets_file(dan="cool") as f:
        secrets = SecretsManager(f, region_name="us-west-1")

    # Check top level decoding
    assert secrets["keep_it_secret"] == "keep_it_safe"
    assert secrets["foo"] == "bar"

    # Check nested decoding
    assert secrets["some_nested_key"]["some_int"] == 123
    assert secrets["some_nested_key"]["some_str"] == "ABC"
    assert secrets["some_nested_key"]["some_enc_str"] == "some_enc_value"

    # Check nested object decoding
    assert secrets["nested_object"] == {"foo": "bar"}
