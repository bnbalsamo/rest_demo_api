from setuptools import setup, find_packages


# Provided Package Metadata
NAME = "rest_demo_api"
DESCRIPTION = "A demo API for use with a APIs/REST presentation."
VERSION = "0.0.1"
AUTHOR = "Brian Balsamo"
AUTHOR_EMAIL = "Brian@BrianBalsamo.com"
URL = 'https://github.com/bnbalsamo/rest_demo_api'
PYTHON_REQUIRES= ">=3"
INSTALL_REQUIRES = [
    "aniso8601==6.0.0",
    "attrs==19.1.0",
    "Click==7.0",
    "environ-config==18.2.0",
    "Flask==1.0.2",
    "Flask-RESTful==0.3.7",
    "Flask-SQLAlchemy==2.3.2",
    "itsdangerous==1.1.0",
    "Jinja2==2.10.1",
    "MarkupSafe==1.1.1",
    "marshmallow==2.19.2",
    "pytz==2019.1",
    "six==1.12.0",
    "SQLAlchemy==1.3.2",
    "Werkzeug==0.15.2"
]
EXTRAS_REQUIRE = {
    # Put "abstract" requirements here
    # See: https://caremad.io/posts/2013/07/setup-vs-requirement/
    # Ex:
    # 'webfrontend': {'flask'}
}

def readme():
    try:
        with open("README.md", 'r') as f:
            return f.read()
    except:
        return False

# Derived Package Metadata
LONG_DESCRIPTION = readme() or DESCRIPTION
if LONG_DESCRIPTION is False:
    LONG_DESCRIPTION = DESCRIPTION
    LONG_DESCRIPTION_CONTENT_TYPE = "text/plain"
else:
    LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"

# Set it up!
setup(
    name=NAME,
    description=DESCRIPTION,
    version=VERSION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(
        exclude=[
            'tests'
        ]
    ),
    # For CLI Scripts, if required
    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
	# },
    include_package_data=True,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=PYTHON_REQUIRES
)
