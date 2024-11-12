from django.db.models.signals import pre_save


FIXTURES_HOOK_IDENTIFIER_ATTRIBUTE_NAME = "is_fixtures_hook"


def fixtures_hook(method):
    setattr(method, FIXTURES_HOOK_IDENTIFIER_ATTRIBUTE_NAME, True)
    return method

def has_fixtures_hook(clazz):
    functions = []
    for attribute_name in dir(clazz):
        attribute = getattr(clazz, attribute_name)
        if callable(attribute) and not attribute_name.startswith("__") and hasattr(attribute, FIXTURES_HOOK_IDENTIFIER_ATTRIBUTE_NAME):
            functions.append(attribute)

    if len(functions) > 0:
        def pre_save_hock(instance, *args, **kwargs):
            if kwargs["raw"]:
                for function in functions:
                    function(instance)

        pre_save.connect(pre_save_hock, sender=clazz)
        return clazz

    raise Exception(
        f"Something went wrong. Perhaps the class {clazz.__name__} lacks a @{fixtures_hook.__name__} decorated method."
    )
