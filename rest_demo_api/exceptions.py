"""Exceptions and Errors."""

import attr


@attr.s
class Error(Exception):
    """Base error class."""

    error_name = attr.ib("Error")
    message = attr.ib("An error occurred!")
    response_code = attr.ib(500, converter=int)
