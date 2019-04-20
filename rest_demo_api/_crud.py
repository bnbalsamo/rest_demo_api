"""
Module for the CRUD operations for Authors and Quotes.

Create
Read/List
Update
Destroy
"""

from datetime import datetime

from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError

from ._db import Author, Quote, get_db
from ._schemas import AUTHOR_SCHEMA, QUOTE_SCHEMA
from .exceptions import Error

db = get_db()


def get_existing(model, pk):
    """
    Retrieve an existing instance of a database model by the primary key.

    :param model: The model of the instance to retrieve
    :param pk: The primary key.

    :returns: The model instance.
    """
    err = Error(
        error_name="EntityDoesNotExistError",
        message="Sorry, that entity doesn't exist yet!",
        response_code=404,
    )
    try:
        entity = model.query.get(pk)
    except IntegrityError:
        raise err
    if not entity:
        raise err
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
        author_data = AUTHOR_SCHEMA.load(author_info).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError", message=err.messages, response_code=422
        )
    if Author.query.filter_by(name=author_data["name"]).first() is not None:
        raise Error(
            error_name="AuthorAlreadyExistsError",
            message="That author already exists!",
            response_code=400,
        )
    author = Author(**author_data)
    author.posted_at = datetime.now()
    db.session.add(author)
    db.session.commit()
    return author


def get_total_number_of_authors():
    """
    Get the total number of author entries in the DB.

    :rtype: int
    """
    return Author.query.count()


def list_authors(limit=50, offset=0):
    """
    List all existing authors.

    :rtype: list[dict]
    :returns: A list of all existing authors.
    """
    authors = Author.query.offset(offset).limit(limit).all()
    return authors


def read_author(pk):
    """
    Get a single author.

    :param int pk: The primary key of the author's db entry.

    :rtype: dict
    :returns: The author entry.
    """
    author = get_existing(Author, pk)
    return author


def update_author(pk, author_info, partial=False):
    """
    Update an existing author.

    :param int pk: The primary key of the author's db entry.
    :param dict author_info: The information to use to update
        the author
    :param bool partial: Whether or not support partial validation.

    :rtype: dict
    :returns: The updated author dictionary
    """
    author = get_existing(Author, pk)
    try:
        author_data = AUTHOR_SCHEMA.load(author_info, partial=partial).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError", message=err.messages, response_code=422
        )
    # Update the object
    for key in author_data:
        setattr(author, key, author_data[key])
    author.updated_at = datetime.now()
    db.session.add(author)
    db.session.commit()
    return author


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
        quote_data = QUOTE_SCHEMA.load(quote_info).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError", message=err.messages, response_code=422
        )
    # Intelligently handle dynamically adding the author if required.
    author = Author.query.filter(Author.name == quote_data["author"]["name"]).first()
    if author is None:
        author = create_author(quote_info["author"])
    else:
        # If the author already exists check the quote is unique
        # in _that author's_ list of quotes.
        if (
            Quote.query.join(Author)
            .filter(Quote.content == quote_data["content"])
            .filter(Author.name == author.name)
            .first()
        ):
            raise Error(
                error_name="QuoteAlreadyExistsError",
                message="That quote already exists!",
                response_code=400,
            )
    # Inject the Author DB object into the data to prep
    # for creating the Quote DB object...
    quote_data["author"] = author
    quote = Quote(**quote_data)
    quote.posted_at = datetime.now()
    db.session.add(quote)
    db.session.commit()
    return quote


def get_total_number_of_quotes():
    """
    Get the total number of quote entries in the DB.

    :rtype: int
    """
    return Author.query.count()


def list_quotes(limit=50, offset=0):
    """
    List all existing quotes.

    :rtype: list[dict]
    :returns: A list of all the quotes.
    """
    quotes = Quote.query.offset(offset).limit(limit).all()
    return quotes


def read_quote(pk):
    """
    Get a single quote.

    :param int pk: The primary key of the quote to get
    :rtype: dict
    :returns: The quote entry.
    """
    quote = get_existing(Quote, pk)
    return quote


def update_quote(pk, quote_info, partial=False):
    """
    Update a quote.

    :param int pk: The primary key of the quote to update.
    :param dict quote_info: Information to use to update the quote entry.
    :param bool partial: Whether or not support partial validation.

    :rtype: dict
    :returns: The updated quote entry.
    """
    quote = get_existing(Quote, pk)
    try:
        quote_data = QUOTE_SCHEMA.load(quote_info, partial=partial).data
    except ValidationError as err:
        raise Error(
            error_name="SchemaValidationError", message=err.messages, response_code=422
        )
    if (
        quote_data.get("author")  # pylint: disable=C0330
        and quote_data["author"].get("name")  # pylint: disable=C0330
        and quote_data["author"]["name"] != quote.author.name  # pylint: disable=C0330
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
        setattr(quote, key, quote_data[key])
    quote.updated_at = datetime.now()
    db.session.add(quote)
    db.session.commit()
    return quote


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


def get_total_number_of_author_quotes(pk):
    """
    Get the total number of quotes for this author in the DB.

    :rtype: int
    """
    author = get_existing(Author, pk)
    return Quote.query.join(Author).filter(Author.id == author.id).count()


def list_author_quotes(pk, limit=50, offset=0):
    """
    List quotes by a given author.

    :param int pk: The primary key

    :rtype: list[dict]
    :returns: A list of quotes
    """
    author = get_existing(Author, pk)
    quotes = (
        Quote.query.join(Author)
        .filter(Author.id == author.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return quotes
