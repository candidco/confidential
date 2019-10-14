def merge(initial: dict, overrides: dict, path=None) -> dict:
    """
    Merges overrides into initial

    :param initial: <dict>
    :param overrides: <dict>
    :return: Merged <dict>
    """
    if path is None:
        path = []

    for key in overrides:
        if key in initial:
            if isinstance(initial[key], dict) and isinstance(overrides[key], dict):
                merge(initial[key], overrides[key], path + [str(key)])
            else:
                initial[key] = overrides[key]
        else:
            initial[key] = overrides[key]

    return initial
