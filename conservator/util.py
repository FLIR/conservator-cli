from sgqlc.types import BaseItem


def to_clean_string(o, first=True):
    s = ''
    if isinstance(o, dict):
        s += "{"
        for key, value in o.items():
            s += f"\n{key}: {to_clean_string(value, False)}"
        s += "\n}"
    elif hasattr(o, '__field_names__'):
        for field in o.__field_names__:
            if not hasattr(o, field):
                continue
            value = getattr(o, field)
            s += f"\n{field}: {to_clean_string(value, False)}"
    elif isinstance(o, list) or isinstance(o, tuple):
        s += "["
        for v in o:
            s += f"\n{to_clean_string(v, False)}"
        s += "\n]"
    else:
        s += f"{o}"

    s = s.replace('\n', '\n    ')

    if first and s.startswith('\n'):
        s = s[1:]

    return s


def to_python_field_name(graphql_type, graphql_name):
    for name in graphql_type.__field_names__:
        if BaseItem._to_graphql_name(name) == graphql_name:
            return name
