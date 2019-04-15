"""Schemas."""

from marshmallow import Schema, ValidationError, fields


def must_not_be_blank(data):
    """Validate fields aren't empty."""
    if not data:
        raise ValidationError("Data not provided.")


class AuthorSchema(Schema):
    """Schema for Author objects."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=must_not_be_blank)
    quotes = fields.Nested("NestedQuoteSchema", many=True, exclude=("author",))


class NestedAuthorSchema(Schema):
    """Schema for Author objects embedded in quotes."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=must_not_be_blank)


class QuoteSchema(Schema):
    """Schema for Quote objects."""

    id = fields.Int(dump_only=True)
    author = fields.Nested(NestedAuthorSchema, validate=must_not_be_blank)
    content = fields.Str(required=True, validate=must_not_be_blank)
    posted_at = fields.DateTime(dump_only=True)


class NestedQuoteSchema(Schema):
    """Schema for Quote objects embedded in authors."""

    id = fields.Int(dump_only=True)
    content = fields.Str(required=True, validate=must_not_be_blank)
    posted_at = fields.DateTime(dump_only=True)


AUTHOR_SCHEMA = AuthorSchema()
AUTHORS_SCHEMA = AuthorSchema(many=True, exclude=("quotes",))
QUOTE_SCHEMA = QuoteSchema()
QUOTES_SCHEMA = QuoteSchema(many=True, only=("id", "content"))
