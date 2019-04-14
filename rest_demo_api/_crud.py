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


def create_author(author_info):
    """
    Create a new Author.

    :param dict author_info: The information to use to create
        the new author.

    :rtype: dict
    :returns: The new author entry.
    """
    try:
        data = AUTHOR_SCHEMA.load(author_info).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError",
            message=json.dumps(err.messages),
            response_code=422,
        )
    author = Author.query.filter_by(name=data["name"]).first()
    if author is not None:
        raise Error(
            error_name="AuthorAlreadyExistsError",
            message="That author already exists!",
            response_code=400,
        )
    author = Author(name=data["name"])
    db.session.add(author)
    if data.get("quotes"):
        for quote_dict in data["quotes"]:
            quote = Quote(
                author=author, content=quote_dict["content"], posted_at=datetime.now()
            )
            db.session.add(quote)
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
    try:
        author = Author.query.get(pk)
    except IntegrityError:
        raise Error(
            error_name="AuthorDoesNotExistError",
            message="Sorry, that author doesn't exist yet!",
            response_code=404,
        )
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
    try:
        existing_author = Author.query.get(pk)
    except IntegrityError:
        raise Error(
            error_name="AuthorDoesNotExistError",
            message="Sorry, that author doesn't exist yet!",
            response_code=404,
        )
    try:
        new_data = AUTHOR_SCHEMA.load(author_info).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError",
            message=json.dumps(err.messages),
            response_code=422,
        )
    if new_data.get("quotes"):
        for quote in new_data["quotes"]:
            if quote not in AUTHOR_SCHEMA.dump(existing_author).data["quotes"]:
                raise Error(
                    error_name="CanNotCreateOrEditQuotesFromAuthorUpdate",
                    message="Sorry, it looks like you tried to create or "
                    + "edit a quote while updating an author. You have to use the "
                    + "quotes endpoint for that!",
                    response_code=400,
                )
        new_data.pop("quotes")
    existing_author.name = new_data["name"]
    db.session.add(existing_author)
    db.session.commit()
    return AUTHOR_SCHEMA.dump(existing_author).data


def delete_author(pk):
    """
    Delete an author entry.

    :param int pk: The primary key of the author to delete
    """
    try:
        existing_author = Author.query.get(pk)
    except IntegrityError:
        raise Error(
            error_name="AuthorDoesNotExistError",
            message="Sorry, that author doesn't exist yet!",
            response_code=404,
        )
    db.session.delete(existing_author)
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
        data = QUOTE_SCHEMA.load(quote_info).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError",
            message=json.dumps(err.messages),
            response_code=422,
        )
    # TODO: Better measure of uniqueness?
    quote = Quote.query.filter_by(content=data["content"]).first()
    if quote is not None:
        raise Error(
            error_name="QuoteAlreadyExistsError",
            message="That quote already exists!",
            response_code=400,
        )
    author = Author.query.filter_by(name=data["author"]["name"]).first()
    if author is None:
        # Create a new author
        author = Author(name=data["author"]["name"])
        db.session.add(author)
    quote = Quote
    quote = Quote(content=data["content"], author=author, posted_at=datetime.now())
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
    try:
        quote = Quote.query.get(pk)
    except IntegrityError:
        raise Error(
            err_name="QuoteDoesNotExistError",
            message="Sorry, that quote doesn't exist yet!",
            response_code=404,
        )
    return QUOTE_SCHEMA.dump(quote).data


def update_quote(pk, quote_info):
    """
    Update a quote.

    :param int pk: The primary key of the quote to update.
    :param dict quote_info: Information to use to update the quote entry.

    :rtype: dict
    :returns: The updated quote entry.
    """
    try:
        existing_quote = Quote.query.get(pk)
    except IntegrityError:
        raise Error(
            error_name="QuoteDoesNotExistError",
            message="Sorry, that quote doesn't exist yet!",
            response_code=404,
        )
    try:
        new_data = QUOTE_SCHEMA.load(quote_info).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError",
            message=json.dumps(err.messages),
            response_code=422,
        )
    if "author" in new_data:
        if new_data["author"] != QUOTE_SCHEMA.dump(existing_quote).data["author"]:
            raise Error(
                error_name="CanNotCreateOrEditAuthorsFromQuoteUpdate",
                message="Sorry, it looks like you tried to create or "
                + "edit an author while updating a quote. You have to use the "
                + "authors endpoint for that!",
                response_code=400,
            )
        new_data.pop("author")
    existing_quote.content = new_data["content"]
    db.session.add(existing_quote)
    db.session.commit()
    return QUOTE_SCHEMA.dumps(existing_quote).data


def delete_quote(pk):
    """
    Delete a quote entry.

    :param int pk: The primary key of the quote to delete.
    """
    try:
        existing_quote = Quote.query.get(pk)
    except IntegrityError:
        raise Error(
            error_name="QuoteDoesNotExistError",
            message="Sorry, that quote doesn't exist yet!",
            response_code=404,
        )
    db.session.delete(existing_quote)
    db.session.commit()
