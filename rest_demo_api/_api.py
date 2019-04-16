"""Endpoints for the API."""

# pylint: disable=R0201

from flask import Response, jsonify, request
from flask_restful import Api, Resource

from ._crud import (
    create_author,
    create_author_quote,
    create_quote,
    delete_author,
    delete_quote,
    list_author_quotes,
    list_authors,
    list_quotes,
    read_author,
    read_quote,
    update_author,
    update_quote,
)
from .exceptions import Error

_CACHED_API = None


def get_api():
    """
    Return the API Object.

    Additionally, handles caching it in the module namespace.

    :returns: The api object
    """
    global _CACHED_API  # pylint: disable=W0603
    if _CACHED_API is not None:
        return _CACHED_API
    api = Api()
    api.add_resource(Root, "/")
    api.add_resource(Authors, "/authors")
    api.add_resource(Author, "/authors/<int:pk>")
    api.add_resource(AuthorQuotes, "/authors/<int:pk>/quotes")
    api.add_resource(Quotes, "/quotes")
    api.add_resource(Quote, "/quotes/<int:pk>")
    api.add_resource(LivenessCheck, "/-/alive")
    api.add_resource(HealthCheck, "/-/healthy")
    _CACHED_API = api
    return api


def get_request_json(required=True):
    """
    Get the JSON body of a request.

    :param bool required: If true, throw an error if there is no JSON body.

    :rtype: dict
    :returns: The JSON body of the request
    """
    rjson = request.get_json()
    if not rjson and required:
        raise Error(
            error_name="NoDataError",
            message="You didn't submit any JSON data!",
            response_code=400,
        )
    return rjson


class Root(Resource):
    """A mapping of the API."""

    def get(self):
        """
        Return the layout of the API.

        :rtype: flask.Response
        """
        return {"authors": "/authors{/id}", "quotes": "/quotes{/id}"}


class Authors(Resource):
    """Functionality for the Authors collection."""

    def get(self):
        """
        Return a list of authors.

        :rtype: flask.Response
        """
        # TODO: Pagination?
        author_list = list_authors()
        return jsonify(author_list)

    def post(self):
        """
        Create a new author entry.

        :rtype: flask.Response
        """
        rjson = get_request_json()
        new_author = create_author(rjson)
        return jsonify(new_author)


class Author(Resource):
    """Functionality for Author instances."""

    def get(self, pk):
        """
        Return an author entry.

        :rtype: flask.Response
        """
        author = read_author(pk)
        return jsonify(author)

    def put(self, pk):
        """
        Update an author entry.

        :param int pk: The primary key of the author to update.

        :rtype: flask.Response
        """
        rjson = get_request_json()
        updated_author = update_author(pk, rjson)
        return jsonify(updated_author)

    def delete(self, pk):
        """
        Delete an author entry.

        :param int pk: The primary key of te author to delete.

        :rtype: flask.Response
        """
        delete_author(pk)
        return Response(status=204)


class AuthorQuotes(Resource):
    """Quotes endpoint with an implicit author."""

    def get(self, pk):
        """
        Get a list of quotes from an author.

        :param int pk: The primary key of the author.

        :rtype: flask.Response
        :returns: The list of quotes by the provided author.
        """
        author_quote_list = list_author_quotes(pk)
        return jsonify(author_quote_list)

    def post(self, pk):
        """
        Create a quote with an implicit author.

        :param int pk: The primary key of the author.

        :rtype: flask.Response
        :returns: The new quote entry.
        """
        rjson = get_request_json()
        new_author_quote = create_author_quote(pk, rjson)
        return jsonify(new_author_quote)


class Quotes(Resource):
    """Functionality for the Quotes collection."""

    def get(self):
        """
        Get a list of all the quotes.

        :rtype: flask.Response
        """
        # TODO: Pagination?
        quote_list = list_quotes()
        return jsonify(quote_list)

    def post(self):
        """
        Create a new quote entry.

        :rtype: flask.Response
        """
        rjson = get_request_json()
        new_quote = create_quote(rjson)
        return jsonify(new_quote)


class Quote(Resource):
    """Functionality for Quote instances."""

    def get(self, pk):
        """
        Get a quote entry.

        :param int pk: The primary key of the quote.

        :rtype: flask.Response
        """
        quote = read_quote(pk)
        return jsonify(quote)

    def delete(self, pk):
        """
        Delete a quote.

        :param int pk: The primary key of the quote.

        :rtype: flask.Response
        """
        delete_quote(pk)
        return Response(status=204)

    def put(self, pk):
        """
        Update a quote.

        :paran int pk: The primary key of the quote.

        :rtype: flask.Response
        """
        rjson = get_request_json()
        updated_quote = update_quote(pk, rjson)
        return jsonify(updated_quote)


class LivenessCheck(Resource):
    """Liveness endpoint."""

    def get(self):
        """Return whether or not the application is alive."""
        return Response(status=204)


class HealthCheck(Resource):
    """Health check endpoint."""

    def get(self):
        """Return whether or not the application is healthy."""
        # TODO: Check DB connection
        return Response(status=204)
