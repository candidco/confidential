from confidential.utils import merge


def test_combine():
    initial = {"dang": "bang", "foo": "bar", "node": {"a": "1", "b": "1", "c": {"something": "else"}}}
    overrides = {"foo": "boo", "key_not_in_initial": 3, "node": {"b": "2", "c": "3"}}

    merged = merge(initial, overrides)

    assert merged["dang"] == "bang"
    assert merged["foo"] == "boo"
    assert merged["key_not_in_initial"] == 3
    assert merged["node"]["a"] == "1"
    assert merged["node"]["b"] == "2"
    assert merged["node"]["c"] == "3"
