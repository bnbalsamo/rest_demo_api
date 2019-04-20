"""Database logic + Models."""

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


db = get_db()


class Author(db.Model):  # pylint: disable=R0903
    """Author database model."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    posted_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    date_of_birth = db.Column(db.Date)
    date_of_death = db.Column(db.Date)


class Quote(db.Model):  # pylint: disable=R0903
    """Quote database model."""

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    author = db.relationship("Author", backref=db.backref("quotes", lazy="dynamic"))
    posted_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    context = db.Column(db.String(500))
