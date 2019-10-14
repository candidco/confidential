def merge(initial: dict, overrides: dict) -> dict:
    """
    Merges overrides into initial

    :param initial: <dict>
    :param overrides: <dict>
    :return: Merged <dict>
    """
    for key in overrides:
        if key in initial:
            if isinstance(initial[key], dict) and isinstance(overrides[key], dict):
                merge(initial[key], overrides[key])
            else:
                initial[key] = overrides[key]
        else:
            initial[key] = overrides[key]

    return initial
