import re


_camel_to_snake_case_pattern = re.compile(r"([A-Z])")
_snake_case_to_camel_pattern = re.compile(r"(^([a-z])|_([a-z]))")


def camel_case_string_to_snake_case_string(s):
    first_letter = True

    def add_underscore(letter):
        nonlocal first_letter
        if first_letter:
            first_letter = False
            return letter
        return "_" + letter

    return _camel_to_snake_case_pattern.sub(lambda x: add_underscore(x.group(1).lower()), s)


def snake_case_string_to_camel_case_string(s):
    return _snake_case_to_camel_pattern.sub(lambda x: x.group(1).upper(), s)


def camel_case_class_to_snake_case_string(o):
    return camel_case_string_to_snake_case_string(o.__name__)


def camel_case_instance_to_snake_case_string(o):
    return camel_case_class_to_snake_case_string(o.__class__)


# Copied from "base64.py".
_b32alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def base32_numeric_identifier_split(numeric_identifier):
    return _b32alphabet[numeric_identifier % 32]
