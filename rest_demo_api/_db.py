"""Database logic."""

from flask_sqlalchemy import SQLAlchemy

_CACHED_DB = None


def get_db():
    """
    Return the database object.

    Additionally, handles caching it in the module namespace.

    :returns: The database object
    """
    # Handle caching in the module namespace
    global _CACHED_DB  # pylint: disable=W0603
    if _CACHED_DB is not None:
        return _CACHED_DB
    database = SQLAlchemy()
    _CACHED_DB = database
    return database
