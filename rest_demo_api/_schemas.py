"""Schemas."""

from marshmallow import Schema, ValidationError, fields, post_load

from ._models import Author, Quote


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

    @post_load
    def make_author(self, data):  # pylint: disable=R0201
        """Load a DB instance, instead of a dict."""
        return Author(**data)


class QuoteSchema(Schema):
    """Schema for Quote objects."""

    class Meta:  # pylint: disable=C0111,R0903
        """Inner Config class."""

        strict = True

    id = fields.Int(dump_only=True)
    author = fields.Nested(
        AuthorSchema, required=True, validate=must_not_be_blank, exclude=("quotes",)
    )
    content = fields.Str(required=True, validate=must_not_be_blank)
    posted_at = fields.DateTime(dump_only=True)
    url = fields.Method("get_url", dump_only=True)

    def get_url(self, quote):  # pylint: disable=R0201
        """Produce the URL for the Quote."""
        # Bit of weirdness to avoid a cyclic import...
        from ._api import get_api
        from ._api import Quote as QuoteEndpoint

        api = get_api()
        return api.url_for(QuoteEndpoint, pk=quote.id)

    @post_load
    def make_quote(self, data):  # pylint: disable=R0201
        """Load a DB instance, instead of a dict."""
        return Quote(**data)


AUTHOR_SCHEMA = AuthorSchema()
AUTHORS_SCHEMA = AuthorSchema(many=True, only=("name", "id", "url"))
QUOTE_SCHEMA = QuoteSchema()
QUOTES_SCHEMA = QuoteSchema(many=True, only=("id", "url", "content"))
