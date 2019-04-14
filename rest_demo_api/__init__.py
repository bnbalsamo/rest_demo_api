"""rest_demo_api: A demo API for use with a APIs/REST presentation."""

__author__ = "Brian Balsamo"
__email__ = "Brian@BrianBalsamo.com"
__version__ = "0.0.1"

import logging

import attr
from flask import Flask, jsonify
from flask_restful import Api

from ._config import get_config
from ._db import get_db
from ._endpoints import Author, Authors, HealthCheck, LivenessCheck, Quote, Quotes, Root
from .exceptions import Error

_CACHED_APP = None


def _handle_errors(error):
    response = jsonify(attr.asdict(error))
    response.status_code = error.response_code
    return response


def get_app(config=None):
    """
    Return the WSGI application object.

    :param config: A custom configuration object to use in place
        of the configuration object generated from the environment.

    :returns: The WSGI application object.
    """
    # Handle caching in the module namespace
    global _CACHED_APP  # pylint: disable=W0603
    if _CACHED_APP is not None:
        return _CACHED_APP

    # Create a new application instance
    app_instance = Flask(__name__.split(".")[0])
    _CACHED_APP = app_instance

    # Register error handling
    app_instance.register_error_handler(Error, _handle_errors)

    # Configure
    if config is None:
        config = get_config()
    app_instance.config.from_object(config.flask)

    # Init DB
    database = get_db()
    database.init_app(app_instance)
    with app_instance.app_context():
        database.create_all()

    # Init API
    api = Api(app_instance)
    api.add_resource(Root, "/")
    api.add_resource(Authors, "/authors")
    api.add_resource(Author, "/authors/<int:pk>")
    api.add_resource(Quotes, "/quotes")
    api.add_resource(Quote, "/quotes/<int:pk>")
    api.add_resource(LivenessCheck, "/-/alive")
    api.add_resource(HealthCheck, "/-/healthy")

    # Configure Logging
    logging.basicConfig(level=config.verbosity)

    return app_instance


__all__ = ["get_app", "exceptions"]
