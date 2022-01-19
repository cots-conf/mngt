"""Schema for the API endpoints."""
from marshmallow import Schema, fields


class PresentationSchema(Schema):
    """Schema for the presetntation."""

    participant_id = fields.Int()
    role = fields.Str()
    order = fields.Int()


class NewPanelSchema(Schema):
    """Schema for the panel."""

    name = fields.Str(required=True)
    start = fields.DateTime(required=True)
    duration = fields.Int(required=True)
    gap = fields.Int(required=True)

    presentations = fields.Nested(PresentationSchema(many=True))
