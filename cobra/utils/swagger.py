import types

from drf_yasg.utils import swagger_auto_schema


def configure_swagger(cls):
    swagger_methods_data = getattr(cls, "swagger_methods_data", {})
    for method_name, data in swagger_methods_data.items():
        if isinstance(method := getattr(cls, method_name), types.FunctionType):
            setattr(cls, method_name, swagger_auto_schema(**data)(method))
    return cls
