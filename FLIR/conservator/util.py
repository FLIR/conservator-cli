def to_clean_string(o, first=True):
    s = ''
    if isinstance(o, dict):
        s += "{"
        for key, value in o.items():
            s += f"\n{key}: {to_clean_string(value, False)}"
        s = s.replace('\n', '\n    ')
        s += "\n}"
    elif hasattr(o.__class__, 'underlying_type'):
        for field in o.underlying_type.__field_names__:
            if not hasattr(o, field):
                continue
            value = getattr(o, field)
            s += f"\n{field}: {to_clean_string(value, False)}"
        s = s.replace('\n', '\n    ')

    elif hasattr(o, '__field_names__'):
        for field in o.__field_names__:
            if not hasattr(o, field):
                continue
            value = getattr(o, field)
            s += f"\n{field}: {to_clean_string(value, False)}"
        s = s.replace('\n', '\n    ')
    elif isinstance(o, list) or isinstance(o, tuple):
        s += "["
        for v in o:
            s += f"\n{to_clean_string(v, False)}"
        s = s.replace('\n', '\n    ')
        s += "\n]"
    else:
        s += f"{o}"
        s = s.replace('\n', '\n    ')

    if first and s.startswith('\n'):
        s = s[1:]

    return s
