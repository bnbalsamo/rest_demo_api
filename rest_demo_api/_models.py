"""Database models."""

from ._db import get_db

db = get_db()


class Author(db.Model):  # pylint: disable=R0903
    """Author database model."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))


class Quote(db.Model):  # pylint: disable=R0903
    """Quote database model."""

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    author = db.relationship("Author", backref=db.backref("quotes", lazy="dynamic"))
    posted_at = db.Column(db.DateTime)
