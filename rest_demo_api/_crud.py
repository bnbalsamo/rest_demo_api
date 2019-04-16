"""
Module for the CRUD operations for Authors and Quotes.

Create
Read/List
Update
Destroy
"""

import json
from datetime import datetime

from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError

from ._db import get_db
from ._models import Author, Quote
from ._schemas import AUTHOR_SCHEMA, AUTHORS_SCHEMA, QUOTE_SCHEMA, QUOTES_SCHEMA
from .exceptions import Error

db = get_db()


def get_existing(model, pk):
    """
    Retrieve an existing instance of a database model by the primary key.

    :param model: The model of the instance to retrieve
    :param pk: The primary key.

    :returns: The model instance.
    """
    try:
        entity = model.query.get(pk)
    except IntegrityError:
        raise Error(
            error_name="EntityDoesNotExistError",
            message="Sorry, that entity doesn't exist yet!",
            response_code=404,
        )
    return entity


def create_author(author_info):
    """
    Create a new Author.

    :param dict author_info: The information to use to create
        the new author.

    :rtype: dict
    :returns: The new author entry.
    """
    try:
        author = AUTHOR_SCHEMA.load(author_info).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError",
            message=json.dumps(err.messages),
            response_code=422,
        )
    if Author.query.filter_by(name=author.name).first() is not None:
        raise Error(
            error_name="AuthorAlreadyExistsError",
            message="That author already exists!",
            response_code=400,
        )
    db.session.add(author)
    db.session.commit()
    return AUTHOR_SCHEMA.dump(author).data


def list_authors():
    """
    List all existing authors.

    :rtype: list[dict]
    :returns: A list of all existing authors.
    """
    authors = Author.query.all()
    return AUTHORS_SCHEMA.dump(authors).data


def read_author(pk):
    """
    Get a single author.

    :param int pk: The primary key of the author's db entry.

    :rtype: dict
    :returns: The author entry.
    """
    author = get_existing(Author, pk)
    return AUTHOR_SCHEMA.dump(author).data


def update_author(pk, author_info):
    """
    Update an existing author.

    :param int pk: The primary key of the author's db entry.
    :param dict author_info: The information to use to update
        the author

    :rtype: dict
    :returns: The updated author dictionary
    """
    author = get_existing(Author, pk)
    errors = AUTHOR_SCHEMA.validate(author_info, partial=True)
    if errors:
        raise Error(
            error_name="SchemaValidationError",
            message=json.dumps(errors),
            response_code=422,
        )
    # Update the object
    for key in author_info:
        setattr(author, key, author_info[key])
    db.session.add(author)
    db.session.commit()
    return AUTHOR_SCHEMA.dump(author).data


def delete_author(pk):
    """
    Delete an author entry.

    :param int pk: The primary key of the author to delete
    """
    author = get_existing(Author, pk)
    # TODO: Replace with a cascade in the model?
    for quote in author.quotes:
        db.session.delete(quote)
    db.session.delete(author)
    db.session.commit()


def create_quote(quote_info):
    """
    Create a new quote entry.

    :param dict quote_info: The information to use to build the new
        quote entry.

    :rtype: dict
    :returns: The new quote entry
    """
    try:
        quote = QUOTE_SCHEMA.load(quote_info).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError",
            message=json.dumps(err.messages),
            response_code=422,
        )
    author = Author.query.filter_by(name=quote.author.name).first()
    if author is None:
        # Create a new author
        author = Author(name=quote.author.name)
        db.session.add(author)
    else:
        # Prevent quotes with duplicate content under the same author
        same_quotes = Quote.query.filter_by(
            author=author, content=quote.content
        ).first()
        if same_quotes:
            raise Error(
                error_name="QuoteAlreadyExistsError",
                message="That quote already exists!",
                response_code=400,
            )
    quote.posted_at = datetime.now()
    db.session.add(quote)
    db.session.commit()
    return QUOTE_SCHEMA.dump(quote).data


def list_quotes():
    """
    List all existing quotes.

    :rtype: list[dict]
    :returns: A list of all the quotes.
    """
    quotes = Quote.query.all()
    return QUOTES_SCHEMA.dump(quotes).data


def read_quote(pk):
    """
    Get a single quote.

    :param int pk: The primary key of the quote to get
    :rtype: dict
    :returns: The quote entry.
    """
    quote = get_existing(Quote, pk)
    return QUOTE_SCHEMA.dump(quote).data


def update_quote(pk, quote_info):
    """
    Update a quote.

    :param int pk: The primary key of the quote to update.
    :param dict quote_info: Information to use to update the quote entry.

    :rtype: dict
    :returns: The updated quote entry.
    """
    quote = get_existing(Quote, pk)
    errors = QUOTE_SCHEMA.validate(quote_info, partial=True)
    if errors:
        raise Error(
            error_name="SchemaValidationError",
            message=json.dumps(errors),
            response_code=422,
        )
    if (
        quote_info.get("author")  # pylint: disable=C0330
        and quote_info["author"].get("name")  # pylint: disable=C0330
        and quote_info["author"]["name"] != quote.author.name  # pylint: disable=C0330
    ):
        raise Error(
            error_name="CanNotCreateOrEditAuthorsFromQuoteUpdate",
            message="Sorry, it looks like you tried to create or "
            + "edit an author while updating a quote. You have to use the "
            + "authors endpoint for that!",
            response_code=400,
        )
    for key in quote_info:
        if key == "author":
            continue
        setattr(quote, key, quote_info[key])
    db.session.add(quote)
    db.session.commit()
    return QUOTE_SCHEMA.dump(quote).data


def delete_quote(pk):
    """
    Delete a quote entry.

    :param int pk: The primary key of the quote to delete.
    """
    quote = get_existing(Quote, pk)
    db.session.delete(quote)
    db.session.commit()


def create_author_quote(pk, quote_info):
    """
    Create a quote with the author implicitly specified.

    :param int pk: The primary key.
    :param dict quote_info: The information for the quote entry.

    :rtype: dict
    :returns: The new quote entry
    """
    author = get_existing(Author, pk)
    # Insert the author
    quote_info["author"] = AUTHOR_SCHEMA.dump(author).data
    return create_quote(quote_info)


def list_author_quotes(pk):
    """
    List quotes by a given author.

    :param int pk: The primary key

    :rtype: list[dict]
    :returns: A list of quotes
    """
    author = get_existing(Author, pk)
    return QUOTES_SCHEMA.dump(author.quotes).data
