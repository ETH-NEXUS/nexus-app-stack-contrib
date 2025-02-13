from functools import wraps


def add_objects_to_kwargs(objects_dict):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for key, value in objects_dict.items():
                kwargs[key] = value
            return func(*args, **kwargs)
        return wrapper
    return decorator
