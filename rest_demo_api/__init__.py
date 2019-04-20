"""rest_demo_api: A demo API for use with a APIs/REST presentation."""

__author__ = "Brian Balsamo"
__email__ = "Brian@BrianBalsamo.com"
__version__ = "0.0.1"

import logging

import attr
from flask import Flask, jsonify

from ._api import get_api
from ._config import get_config
from ._db import get_db
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
    if not config.skip_db_setup:
        with app_instance.app_context():
            database.create_all()

    # Init API
    api = get_api()
    # Kind of hacky, but otherwise flask-restful steps
    # on some toes while handling errors and doesn't provide
    # a great interface to force it to get out of the way.
    api.handle_error = _handle_errors
    api.init_app(app_instance)

    # Configure Logging
    logging.basicConfig(level=config.verbosity)

    return app_instance


__all__ = ["get_app", "exceptions"]
