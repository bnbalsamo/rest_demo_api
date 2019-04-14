"""Endpoints for the API."""

# pylint: disable=R0201

from flask import Response, jsonify, request
from flask_restful import Resource

from ._crud import (
    create_author,
    create_quote,
    delete_author,
    delete_quote,
    list_authors,
    list_quotes,
    read_author,
    read_quote,
    update_author,
    update_quote,
)
from .exceptions import Error


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
        return jsonify(list_authors())

    def post(self):
        """
        Create a new author entry.

        :rtype: flask.Response
        """
        rjson = request.get_json()
        if not rjson:
            raise Error(
                error_name="NoDataError",
                message="You didn't submit any JSON data!",
                response_code=400,
            )
        new_author = create_author(rjson)
        return jsonify(new_author)


class Author(Resource):
    """Functionality for Author instances."""

    def get(self, pk):
        """
        Return an author entry.

        :rtype: flask.Response
        """
        return jsonify(read_author(pk))

    def put(self, pk):
        """
        Update an author entry.

        :param int pk: The primary key of the author to update.

        :rtype: flask.Response
        """
        rjson = request.get_json()
        if not rjson:
            raise Error(
                error_name="NoDataError",
                message="You didn't submit any JSON data!",
                response_code=400,
            )
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


class Quotes(Resource):
    """Functionality for the Quotes collection."""

    def get(self):
        """
        Get a list of all the quotes.

        :rtype: flask.Response
        """
        # TODO: Pagination?
        return jsonify(list_quotes())

    def post(self):
        """
        Create a new quote entry.

        :rtype: flask.Response
        """
        rjson = request.get_json()
        if not rjson:
            raise Error(
                error_name="NoDataError",
                message="You didn't submit any JSON data!",
                response_code=400,
            )
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
        return jsonify(read_quote(pk))

    def put(self, pk):
        """
        Update a quote entry.

        :param int pk: The primary key of the quote.

        :rtype: flask.Response
        """
        rjson = request.get_json()
        if not rjson:
            raise Error(
                error_name="NoDataError",
                message="You didn't submit any JSON data!",
                response_code=400,
            )
        updated_quote = update_quote(pk, rjson)
        return jsonify(updated_quote)

    def delete(self, pk):
        """
        Delete a quote.

        :param int pk: The primary key of the quote.

        :rtype: flask.Response
        """
        delete_quote(pk)
        return Response(status=204)


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
