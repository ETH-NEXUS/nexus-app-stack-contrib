import inspect
from functools import wraps

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.forms.models import model_to_dict

from django_udf_model import Command
from django_udf_model.models import create_dynamic_udf_model


def rpc_udf(field_names=None, _command=Command.SELECT):
    def decorator(func):
        signature = inspect.signature(func)
        udf = func(**{p: None for p in signature.parameters})
        parameters = [p.name for p in signature.parameters.values()]

        nonlocal field_names
        if _command == Command.SELECT and field_names is None:
            FunctionReturnTable = create_dynamic_udf_model(
                "function_return_table",
                {field_name: models.CharField(max_length=100) for field_name in ("column_name", "column_type", "column_number")},
                ("function", "parameters")
            )
            function=f"select_{udf if udf else func.__name__}"
            queryset = FunctionReturnTable.objects.all().table_function(function=function, parameters=parameters)
            if len(queryset) > 0:
                field_names = [row.column_name for row in queryset]
            else:
                raise Exception(f"No return columns found for function: {function}")
        elif _command == Command.INSERT or _command == Command.UPDATE:
            field_names = parameters

        def get_field(name):
            match name:
                case "id":
                    return models.CharField(max_length=100, primary_key=True)
                case _:
                    return models.CharField(max_length=100)

        fields = {field_name: get_field(field_name) for field_name in field_names}
        Tmp = create_dynamic_udf_model(udf if udf else func.__name__, fields, parameters)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_arguments = signature.bind(*args, **kwargs)
            match _command:
                case Command.INSERT:
                    queryset = Tmp.objects.create(**dict(bound_arguments.arguments))
                    return model_to_dict(queryset)
                case Command.UPDATE:
                    queryset = Tmp.objects.update(**dict(bound_arguments.arguments))
                    return queryset
                case Command.DELETE:
                    if isinstance(args[0], list):
                        Tmp.objects.filter(ids__in=args[0]).delete()
                        return None
                    raise ValueError("The ids parameter must be an array.")
                case _:
                    queryset = Tmp.objects.all().table_function(**dict(bound_arguments.arguments))
                    return list((model_to_dict(o) for o in queryset))
        return wrapper
    return decorator


def rpc_udf_insert(field_names=None):
    return rpc_udf(field_names, _command=Command.INSERT)


def rpc_udf_update(field_names=None):
    return rpc_udf(field_names, _command=Command.UPDATE)


def rpc_udf_delete():
    return rpc_udf(field_names=("ids",), _command=Command.DELETE)


class BypassDjangoJSONEncoderValue:
    def __init__(self, value):
        self.value = value


class BypassDjangoJSONEncoder(DjangoJSONEncoder):
    def iterencode(self, o, _one_shot=False):
        if "result" in o:
            result = o["result"]
            if isinstance(result, BypassDjangoJSONEncoderValue):
                del o["result"]
                jsonrpc_message_beginning = str(super().iterencode(o, _one_shot=_one_shot))[2:-3]
                def bypass_iterencode():
                    yield jsonrpc_message_beginning
                    yield ',"result": ['
                    try:
                        yield next(result.value)["data"]
                        for v in result.value:
                            yield ','
                            yield v["data"]
                    except StopIteration:
                        pass
                    yield ']}'
                return bypass_iterencode()
        return super().iterencode(o, _one_shot=_one_shot)


def rpc_udf_json(bypass=False):
    def decorator(func):
        signature = inspect.signature(func)
        udf = func(**{p: None for p in signature.parameters})
        parameters = [p.name for p in signature.parameters.values()]
        Tmp = create_dynamic_udf_model(udf if udf else func.__name__,
                                       {"data": models.TextField() if bypass else models.JSONField()}, parameters)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_arguments = signature.bind(*args, **kwargs)
            queryset = Tmp.objects.all().table_function(**dict(bound_arguments.arguments)).values("data")
            # TODO Use StreamingHttpResponse.
            if bypass:
                return BypassDjangoJSONEncoderValue(queryset.iterator(chunk_size=1000))
            else:
                return list((row["data"] for row in queryset.iterator(chunk_size=1000)))
        return wrapper
    return decorator
