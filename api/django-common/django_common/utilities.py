import re

_camel_to_snake_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_case_string_to_snake_case_string(s):
    return _camel_to_snake_case_pattern.sub("_", s).lower()


def camel_case_class_to_snake_case_string(o):
    return camel_case_string_to_snake_case_string(o.__name__)


def camel_case_instance_to_snake_case_string(o):
    return camel_case_class_to_snake_case_string(o.__class__)


# Copied from "base64.py".
_b32alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def base32_numeric_identifier_split(numeric_identifier):
    return _b32alphabet[numeric_identifier % 32]


def call_all_base_class_methods_until_not_none(o, method_name, *args, **kwargs):
    result = getattr(super(o.__class__, o), method_name)(*args, **kwargs)
    if result is None:
        result = call_all_except_first_base_class_methods_until_not_none(o, method_name, *args, **kwargs)
    return result


def call_all_except_first_base_class_methods_until_not_none(o, method_name, *args, **kwargs):
    for c in o.__class__.__bases__[:-1]:
        result = getattr(super(c, o), method_name)(*args, **kwargs)
        if result is not None:
            return result
    return None
