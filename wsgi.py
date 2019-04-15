"""WSGI bootstrap file."""

from rest_demo_api import get_app

app = get_app()  # pylint: disable=C0103
application = app  # pylint: disable=C0103
