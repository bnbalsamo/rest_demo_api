"""Functionality for generating an OpenAPIv3 spec."""
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from . import __version__, get_app


def get_spec():
    """
    Produce the OpenAPIv3 spec document.

    :rtype: dict
    """
    spec = APISpec(
        title="rest-demo-api",
        version=__version__,
        openapi_version="3.0.2",
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
    )

    spec.components.schema("MiniAuthor", schema="MiniAuthorSchema")
    app = get_app()
    # Useful for debugging
    # print(app.view_functions)
    spec.path("/authors", view=app.view_functions["authors"], app=app)
    spec.path("/authors/{author_id}", view=app.view_functions["author"], app=app)
    spec.path(
        "/authors/{author_id}/quotes", view=app.view_functions["authorquotes"], app=app
    )
    spec.path("/quotes", view=app.view_functions["quotes"], app=app)
    spec.path("/quotes/{quote_id}", view=app.view_functions["quote"], app=app)
    return spec.to_dict()
