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


def call_method_of_all_base_class_and_overwrite_argument(o, method_name, argument):
    for c in o.__class__.__bases__:
        argument = getattr(super(c, o), method_name)(argument)
    return argument


def call_method_of_all_base_class_after_myself_and_overwrite_argument(myself_type, o, method_name, argument):
    check = False
    for c in o.__class__.__bases__:
        if c == myself_type:
            check = True
        if check:
            argument = getattr(super(c, o), method_name)(argument)
    return argument


def call_method_of_all_base_class_until_not_none(o, method_name, *args, **kwargs):
    for c in o.__class__.__bases__:
        result = getattr(super(c, o), method_name)(*args, **kwargs)
        if result is not None:
            return result
    return None


def call_method_of_all_base_class_after_myself_until_not_none(myself_type, o, method_name, *args, **kwargs):
    check = False
    for c in o.__class__.__bases__:
        if c == myself_type:
            check = True
        if check:
            result = getattr(super(c, o), method_name)(*args, **kwargs)
            if result is not None:
                return result
    return None
