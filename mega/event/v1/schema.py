from marshmallow import Schema, fields, post_load, EXCLUDE, post_dump

from mega.event.v1 import PROTOCOL_VERSION, PROTOCOL_NAME
from mega.event.v1.payload import MegaPayload, MegaObject, MegaEvent


class MegaSchemaError(Exception):
    pass


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    @post_dump
    def remove_empty_attributes(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value not in (None, {})
        }


class MegaEventSchema(BaseSchema):
    name = fields.String(required=True, allow_none=False)
    timestamp = fields.DateTime(format='iso', required=True, allow_none=False)
    version = fields.Integer(required=False, allow_none=True, default=1)
    domain = fields.String(required=False, allow_none=True, default=None)
    subject = fields.String(required=False, allow_none=True, default=None)
    publisher = fields.String(required=False, allow_none=True, default=None)
    attributes = fields.Dict(keys=fields.String(), required=False, allow_none=True, default={})

    @post_load
    def build_object(self, data, **kwargs):
        return MegaEvent(**data)

    def handle_error(self, exc, data, **kwargs):
        raise MegaSchemaError("Invalid MEGA payload. There is an error in the 'event' section: {0}".format(exc))


class MegaObjectSchema(BaseSchema):
    type = fields.String(required=False, allow_none=True, default=None)
    id = fields.String(required=False, allow_none=True, default=None)
    version = fields.Integer(required=False, allow_none=True, default=1)
    current = fields.Dict(required=True, allow_none=False)
    previous = fields.Dict(required=False, allow_none=True, default=None)

    @post_load
    def build_object(self, data, **kwargs):
        return MegaObject(**data)

    def handle_error(self, exc, data, **kwargs):
        raise MegaSchemaError("Invalid MEGA payload. There is an error in the 'object' section: {0}".format(exc))


class MegaPayloadSchema(BaseSchema):
    protocol = fields.Constant(PROTOCOL_NAME, dump_only=True)
    version = fields.Constant(PROTOCOL_VERSION, dump_only=True)
    event = fields.Nested(MegaEventSchema, required=True)
    object = fields.Nested(MegaObjectSchema, required=False, allow_none=True, default=None)
    extra = fields.Dict(keys=fields.String(), required=False, allow_none=True, default={})

    @post_load
    def build_object(self, data, **kwargs):
        return MegaPayload(**data)

    def handle_error(self, exc, data, **kwargs):
        raise MegaSchemaError("Invalid MEGA payload: {0}".format(exc))


def matches_mega_payload(data: dict) -> bool:
    if not data:
        return False

    return (
            data.get('protocol') == PROTOCOL_NAME and
            data.get('version') == PROTOCOL_VERSION
    )


def deserialize_mega_payload(data: dict) -> MegaPayload:
    return MegaPayloadSchema().load(data)


def serialize_mega_payload(payload: MegaPayload) -> dict:
    schema = MegaPayloadSchema()
    data = schema.dump(payload)
    schema.validate(data)
    return data
