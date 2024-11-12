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
