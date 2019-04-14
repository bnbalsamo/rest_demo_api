"""API Configuration."""

import sys

import environ
from attr.validators import in_


def _gen_secret_key():
    """
    Python version aware secret key generator.

    Uses os.urandom for py<3.6, otherwise sercrets.token_hex.

    :rtype: str
    :returns: a secret key
    """
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 6:
        from secrets import token_hex

        return token_hex(32)
    from os import urandom

    return str(urandom(32))


class Configuration:  # pylint: disable=R0903
    """Root configuration."""

    @environ.config
    class FlaskConfig:  # pylint: disable=R0903
        """Flask specific configuration."""

        SECRET_KEY = environ.var(_gen_secret_key())
        DEBUG = environ.bool_var(False)
        TESTING = environ.bool_var(False)
        SQLALCHEMY_DATABASE_URI = environ.var("sqlite:////tmp/test.db")
        SQLALCHEMY_TRACK_MODIFICATIONS = environ.bool_var(False)

    flask = environ.group(FlaskConfig)
    verbosity = environ.var(
        "WARNING", validator=in_(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"])
    )


def get_config():
    """Return the configuration object."""
    cfg = environ.config(Configuration, prefix="REST_DEMO_API")
    return environ.to_config(cfg)
