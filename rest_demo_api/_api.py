"""Endpoints for the API."""

# pylint: disable=R0201


from flask import Response, jsonify, render_template, request
from flask_restful import Api, Resource

from ._crud import (
    create_author,
    create_author_quote,
    create_quote,
    delete_author,
    delete_quote,
    get_total_number_of_author_quotes,
    get_total_number_of_authors,
    get_total_number_of_quotes,
    list_author_quotes,
    list_authors,
    list_quotes,
    read_author,
    read_quote,
    update_author,
    update_quote,
)
from ._schemas import AUTHOR_SCHEMA, AUTHORS_SCHEMA, QUOTE_SCHEMA, QUOTES_SCHEMA
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
    api.add_resource(Docs, "/docs")
    api.add_resource(Spec, "/spec")
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

    def get(self):  # noqa: D413
        """
        Return a list of authors.

        ---
        description: Get a list of authors.
        parameters:
            - in: query
              name: offset
              schema:
                  type: integer
              description: >-
               The number of items to skip before beginning
               to collect the result set.
            - in: query
              name: limit
              schema:
                  type: integer
              description: The maximum number of items to return.
        responses:
            200:
                description: The list of authors was retrieved.
                content:
                    application/json:
                        schema: AuthorList
            404:
                description: There is no content on the specified page.
        """
        limit = int(request.args.get("limit", 50))
        if limit > 50:
            limit = 50
        offset = int(request.args.get("offset", 0))
        total_num = get_total_number_of_authors()
        if total_num <= offset:
            raise Error(
                error_name="PageNotFound",
                message="No data on that page!",
                response_code=404,
            )
        if offset + limit >= total_num:
            next_page = None
        else:
            next_page = get_api().url_for(Authors, limit=limit, offset=offset + limit)
        author_list = list_authors(limit, offset)
        return jsonify(
            AUTHORS_SCHEMA.dump(
                {
                    "items": author_list,
                    "next_page": next_page,
                    "limit": limit,
                    "offset": offset,
                    "total": total_num,
                }
            ).data
        )

    def post(self):  # noqa: D413
        """
        Create a new author.

        ---
        description: Create an author.
        requestBody:
            description: Data to use to create the author.
            required: true
            content:
                application/json:
                    schema: AuthorSchema
        responses:
            201:
                description: The author was created.
                content:
                    application/json:
                        schema: AuthorSchema
            422:
                description: Schema validation error.
            400:
                description: That author already exists.
        """
        rjson = get_request_json()
        new_author = create_author(rjson)
        resp = jsonify(AUTHOR_SCHEMA.dump(new_author).data)
        resp.status_code = 201
        return resp


class Author(Resource):
    """Functionality for Author instances."""

    def get(self, pk):  # noqa: D413
        """
        Return an author.

        ---
        description: Get an author.
        parameters:
            - in: path
              name: pk
              description: The primary key of the author
              required: true
              schema:
                  type: integer
        responses:
            200:
                description: The author was found.
                content:
                    application/json:
                        schema: AuthorSchema
            404:
                description: An author with that primary key wasn't found.
        """
        author = read_author(pk)
        return jsonify(AUTHOR_SCHEMA.dump(author).data)

    def put(self, pk):  # noqa: D413
        """
        Update an author.

        ---
        description: Update an author.
        parameters:
            - in: path
              name: pk
              description: The primary key of the author
              required: true
              schema:
                  type: integer
        requestBody:
            description: Data to update the author with.
            required: true
            content:
                application/json:
                    schema: AuthorSchema
        responses:
            200:
                description: The author is updated.
                content:
                    application/json:
                        schema: AuthorSchema
            404:
                description: An author with that primary key wasn't found.
            422:
                description: Schema validation error.
        """
        rjson = get_request_json()
        updated_author = update_author(pk, rjson)
        return jsonify(AUTHOR_SCHEMA.dump(updated_author).data)

    def patch(self, pk):  # noqa: D413
        """
        Update a subset of an author's information.

        ---
        description: Partially update an author.
        parameters:
            - in: path
              name: pk
              description: The primary key of the author
              required: true
              schema:
                  type: integer
        requestBody:
            description: Fields to update in the author entry.
            required: true
            content:
                application/json:
                    schema: AuthorSchema
        responses:
            200:
                description: The author is updated.
                content:
                    application/json:
                        schema: AuthorSchema
            404:
                description: An author with that primary key wasn't found.
            422:
                description: Schema validation error.
        """
        rjson = get_request_json()
        updated_author = update_author(pk, rjson, partial=True)
        return jsonify(AUTHOR_SCHEMA.dump(updated_author).data)

    def delete(self, pk):  # noqa: D413
        """
        Delete an author.

        ---
        description: Delete an author.
        parameters:
            - in: path
              name: pk
              description: The primary key of the author
              required: true
              schema:
                  type: integer
        responses:
            204:
                description: The author has been deleted.
            404:
                description: An author with that primary key wasn't found.
        """
        delete_author(pk)
        return Response(status=204)


class AuthorQuotes(Resource):
    """Quotes endpoint with an implicit author."""

    def get(self, pk):  # noqa: D413
        """
        Get a list of quotes by this author.

        ---
        description: Get a list of quotes by the author.
        parameters:
            - in: query
              name: offset
              schema:
                  type: integer
              description: >-
               The number of items to skip before beginning
               to collect the result set.
            - in: query
              name: limit
              schema:
                  type: integer
              description: The maximum number of items to return.
            - in: path
              name: pk
              description: The primary key of the author
              required: true
              schema:
                  type: integer
        responses:
            200:
                description: The quote list was retrieved.
                content:
                    application/json:
                        schema: QuoteList
            404:
                description: >-
                 An author with that primary key wasn't found,
                 or there is no data on the specified page.
        """
        limit = int(request.args.get("limit", 50))
        if limit > 50:
            limit = 50
        offset = int(request.args.get("offset", 0))
        total_num = get_total_number_of_author_quotes(pk)
        if total_num <= offset:
            raise Error(
                error_name="PageNotFound",
                message="No data on that page!",
                response_code=404,
            )
        if offset + limit >= total_num:
            next_page = None
        else:
            next_page = get_api().url_for(
                AuthorQuotes, limit=limit, offset=offset + limit, pk=pk
            )
        author_quote_list = list_author_quotes(pk, limit, offset)
        return jsonify(
            QUOTES_SCHEMA.dump(
                {
                    "items": author_quote_list,
                    "next_page": next_page,
                    "limit": limit,
                    "offset": offset,
                    "total": total_num,
                }
            ).data
        )

    def post(self, pk):  # noqa: D413
        """
        Create a quote by this author.

        ---
        description: Create a quote by this author.
        parameters:
            - in: path
              name: pk
              description: The primary key of the author
              required: true
              schema:
                  type: integer
        requestBody:
            description: Data to create a quote from.
            required: true
            content:
                application/json:
                    schema: QuoteWithImpliedAuthorSchema
        responses:
            201:
                description: The quote was created.
                content:
                    application/json:
                        schema: QuoteSchema
            404:
                description: An author with that primary key wasn't found.
            422:
                description: Schema validation error.
        """
        rjson = get_request_json()
        new_author_quote = create_author_quote(pk, rjson)
        resp = jsonify(QUOTE_SCHEMA.dump(new_author_quote).data)
        resp.status_code = 201
        return resp


class Quotes(Resource):
    """Functionality for the Quotes collection."""

    def get(self):  # noqa: D413
        """
        Get a list of quotes.

        ---
        description: Get list of quotes.
        parameters:
            - in: query
              name: offset
              schema:
                  type: integer
              description: >-
               The number of items to skip before beginning
               to collect the result set.
            - in: query
              name: limit
              schema:
                  type: integer
              description: The maximum number of items to return.
        responses:
            200:
                description: The quote listing was retrieved.
                content:
                    application/json:
                        schema: QuoteList
            404:
                description: There is no content on the specified page.
        """
        limit = int(request.args.get("limit", 50))
        if limit > 50:
            limit = 50
        offset = int(request.args.get("offset", 0))
        total_num = get_total_number_of_quotes()
        if total_num <= offset:
            raise Error(
                error_name="PageNotFound",
                message="No data on that page!",
                response_code=404,
            )
        if offset + limit >= total_num:
            next_page = None
        else:
            next_page = get_api().url_for(Quotes, limit=limit, offset=offset + limit)
        quote_list = list_quotes(limit, offset)
        return jsonify(
            QUOTES_SCHEMA.dump(
                {
                    "items": quote_list,
                    "next_page": next_page,
                    "limit": limit,
                    "offset": offset,
                    "total": total_num,
                }
            ).data
        )

    def post(self):  # noqa: D413
        """
        Create a quote.

        ---
        description: Create a quote.
        requestBody:
            description: Data to create the quote from.
            required: true
            content:
                application/json:
                    schema: QuoteSchema
        responses:
            201:
                description: The quote was created.
                content:
                    application/json:
                        schema: QuoteSchema
            400:
                description: That quote already exists.
            422:
                description: Schema validation error.
        """
        rjson = get_request_json()
        new_quote = create_quote(rjson)
        resp = jsonify(QUOTE_SCHEMA.dump(new_quote).data)
        resp.status_code = 201
        return resp


class Quote(Resource):
    """Functionality for Quote instances."""

    def get(self, pk):  # noqa: D413
        """
        Get a quote.

        ---
        description: Get a quote.
        parameters:
            - in: path
              name: pk
              description: The primary key of the quote
              required: true
              schema:
                  type: integer
        responses:
            200:
                description: The quote was retrieved.
                content:
                    application/json:
                        schema: QuoteSchema
            404:
                description: A quote with that primary key wasn't found.
        """
        quote = read_quote(pk)
        return jsonify(QUOTE_SCHEMA.dump(quote).data)

    def delete(self, pk):  # noqa: D413
        """
        Delete a quote.

        ---
        description: Delete a quote.
        parameters:
            - in: path
              name: pk
              description: The primary key of the quote
              required: true
              schema:
                  type: integer
        responses:
            204:
                description: The quote is deleted.
            404:
                description: A quote with that primary key wasn't found.
        """
        delete_quote(pk)
        return Response(status=204)

    def put(self, pk):  # noqa: D413
        """
        Update a quote.

        ---
        description: Update a quote.
        parameters:
            - in: path
              name: pk
              description: The primary key of the quote
              required: true
              schema:
                  type: integer
        requestBody:
            description: Data to use to update the quote.
            required: true
            content:
                application/json:
                    schema: QuoteSchema
        responses:
            200:
                description: The quote was updated.
                content:
                    application/json:
                        schema: QuoteSchema
            404:
                description: A quote with that primary key wasn't found.
            422:
                description: Schema validation error.
        """
        rjson = get_request_json()
        updated_quote = update_quote(pk, rjson)
        return jsonify(QUOTE_SCHEMA.dump(updated_quote).data)

    def patch(self, pk):  # noqa: D413
        """
        Update a subset of a quote's information.

        ---
        description: Partially update a quote.
        parameters:
            - in: path
              name: pk
              description: The primary key of the quote
              required: true
              schema:
                  type: integer
        requestBody:
            description: Fields to update in the quote entry.
            required: true
            content:
                application/json:
                    schema: QuoteSchema
        responses:
            200:
                description: The quote was updated.
                content:
                    application/json:
                        schema: QuoteSchema
            404:
                description: A quote with that primary key wasn't found.
            422:
                description: Schema validation error.
        """
        rjson = get_request_json()
        updated_quote = update_quote(pk, rjson, partial=True)
        return jsonify(QUOTE_SCHEMA.dump(updated_quote).data)


class LivenessCheck(Resource):
    """Liveness endpoint."""

    def get(self):  # noqa: D413
        """
        Determine if the application is alive.

        ---
        description: Check the application is alive.
        responses:
            204:
                description: It is!
        """
        return Response(status=204)


class HealthCheck(Resource):
    """Health check endpoint."""

    def get(self):  # noqa: D413
        """
        Determine if the application is healthy.

        ---
        description: Check the application is healthy.
        responses:
            204:
                description: It is!
        """
        # TODO: Check DB connection
        return Response(status=204)


class Docs(Resource):
    """Return the docs."""

    def get(self):
        """Get the docs."""
        resp = Response(render_template("docs.html", docs_url=get_api().url_for(Spec)))
        resp.mimetype = "text/html"
        return resp


class Spec(Resource):
    """Return the swagger spec."""

    def get(self):
        """Get the spec."""
        # Avoid a cyclic import...
        from ._spec import get_spec

        return get_spec()
