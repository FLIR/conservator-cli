

def dict_to_clean_string(d, indent=0):
    s = ""
    for key, value in d.items():
        if isinstance(value, dict):
            s += "    " * indent + f"{key}:\n"
            s += dict_to_clean_string(value, indent + 1)
        else:
            s += "    " * indent + f"{key}: {value}\n"
    return s

