"""Schemas."""

from marshmallow import Schema, ValidationError, fields


def must_not_be_blank(data):
    """Validate fields aren't empty."""
    if not data:
        raise ValidationError("Data not provided.")


class AuthorSchema(Schema):
    """Schema for Author objects."""

    class Meta:  # pylint: disable=C0111,R0903
        """Inner Config class."""

        strict = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=must_not_be_blank)
    url = fields.Method("get_url", dump_only=True)
    quotes = fields.Method("get_quotes_url", dump_only=True)
    posted_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    date_of_birth = fields.Date()
    date_of_death = fields.Date()

    def get_url(self, author):  # pylint: disable=R0201
        """Produce the url for the Author."""
        # Bit of weirdness to avoid a cyclic import...
        from ._api import get_api
        from ._api import Author as AuthorEndpoint

        api = get_api()
        return api.url_for(AuthorEndpoint, pk=author.id)

    def get_quotes_url(self, author):  # pylint: disable=R0201
        """Produce the url for the author's quotes."""
        # Bit of weirdness to avoid a cyclic import...
        from ._api import get_api, AuthorQuotes

        api = get_api()
        return api.url_for(AuthorQuotes, pk=author.id)


class MiniAuthorSchema(Schema):
    """Schema for embedded or listed Author objects."""

    class Meta:  # pylint: disable=C0111,R0903
        """Inner Config class."""

        strict = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=must_not_be_blank)
    url = fields.Method("get_url", dump_only=True)

    def get_url(self, author):  # pylint: disable=R0201
        """Produce the url for the Author."""
        # Bit of weirdness to avoid a cyclic import...
        from ._api import get_api
        from ._api import Author as AuthorEndpoint

        api = get_api()
        return api.url_for(AuthorEndpoint, pk=author.id)


class QuoteSchema(Schema):
    """Schema for Quote objects."""

    class Meta:  # pylint: disable=C0111,R0903
        """Inner Config class."""

        strict = True

    id = fields.Int(dump_only=True)
    author = fields.Nested(
        "MiniAuthorSchema", required=True, validate=must_not_be_blank
    )
    content = fields.Str(required=True, validate=must_not_be_blank)
    posted_at = fields.DateTime(dump_only=True)
    url = fields.Method("get_url", dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    context = fields.Str()

    def get_url(self, quote):  # pylint: disable=R0201
        """Produce the URL for the Quote."""
        # Bit of weirdness to avoid a cyclic import...
        from ._api import get_api
        from ._api import Quote as QuoteEndpoint

        api = get_api()
        return api.url_for(QuoteEndpoint, pk=quote.id)


# Required for auto-documentation.
class QuoteWithImpliedAuthorSchema(Schema):
    """Schema for Quote objects with an implied Author."""

    class Meta:  # pylint: disable=C0111,R0903
        """Inner Config class."""

        strict = True

    id = fields.Int(dump_only=True)
    content = fields.Str(required=True, validate=must_not_be_blank)
    posted_at = fields.DateTime(dump_only=True)
    url = fields.Method("get_url", dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    context = fields.Str()

    def get_url(self, quote):  # pylint: disable=R0201
        """Produce the URL for the Quote."""
        # Bit of weirdness to avoid a cyclic import...
        from ._api import get_api
        from ._api import Quote as QuoteEndpoint

        api = get_api()
        return api.url_for(QuoteEndpoint, pk=quote.id)


class MiniQuoteSchema(Schema):
    """Schema for embbeded or listed Quote objects."""

    class Meta:  # pylint: disable=C0111,R0903
        """Inner Config class."""

        strict = True

    id = fields.Int(dump_only=True)
    content = fields.Str(required=True, validate=must_not_be_blank)
    url = fields.Method("get_url", dump_only=True)

    def get_url(self, quote):  # pylint: disable=R0201
        """Produce the URL for the Quote."""
        # Bit of weirdness to avoid a cyclic import...
        from ._api import get_api
        from ._api import Quote as QuoteEndpoint

        api = get_api()
        return api.url_for(QuoteEndpoint, pk=quote.id)


class Paginated(Schema):
    """Base Schema for Paginated things."""

    next_page = fields.Url(relative=True)
    limit = fields.Int(required=True, validator=must_not_be_blank)
    offset = fields.Int(required=True, validator=must_not_be_blank)
    total = fields.Int(required=True)


class AuthorList(Paginated):
    """Author list schema."""

    items = fields.Nested("MiniAuthorSchema", many=True)


class QuoteList(Paginated):
    """Quote list schema."""

    items = fields.Nested("MiniQuoteSchema", many=True)


AUTHOR_SCHEMA = AuthorSchema()
# AUTHORS_SCHEMA = AuthorSchema(many=True, only=("name", "id", "url"))
AUTHORS_SCHEMA = AuthorList()
QUOTE_SCHEMA = QuoteSchema()
# QUOTES_SCHEMA = QuoteSchema(many=True, only=("id", "url", "content"))
QUOTES_SCHEMA = QuoteList()
