from flask import has_request_context, request
from marshmallow import pre_load
from marshmallow.utils import missing

# Partial updates must never overwrite stored values with schema defaults
_PARTIAL_UPDATE_METHODS = ('PATCH', 'PUT')


def patch_defaults(schema, in_data):
    """
    Add the schema's default value for every loadable field that is absent from `in_data`.

    :param schema: marshmallow schema instance
    :param in_data: dict of (already unwrapped) request data
    :return: `in_data` with the missing defaults filled in
    """
    if has_request_context() and request.method in _PARTIAL_UPDATE_METHODS:
        return in_data

    for name, field in schema.fields.items():
        if field.dump_only:
            continue
        if name in in_data or (field.load_from and field.load_from in in_data):
            continue
        default = field.default
        if default is missing:
            continue
        in_data[name] = default() if callable(default) else default

    return in_data


def use_defaults():
    """
    Class decorator for marshmallow schemas: fills in field defaults when loading data
    """
    def wrapper(cls):
        @pre_load
        def _patch_defaults(self, in_data):
            return patch_defaults(self, in_data)

        cls._patch_defaults = _patch_defaults
        # processors are normally resolved at class creation, redo it with the new hook
        cls._resolve_processors()
        return cls

    return wrapper
