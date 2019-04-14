# REST_Demo_API [![v0.0.1](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/bnbalsamo/rest_demo_api/releases) 

[![Build Status](https://travis-ci.org/bnbalsamo/rest_demo_api.svg?branch=master)](https://travis-ci.org/bnbalsamo/rest_demo_api) [![Coverage Status](https://coveralls.io/repos/github/bnbalsamo/rest_demo_api/badge.svg?branch=master)](https://coveralls.io/github/bnbalsamo/rest_demo_api?branch=master) [![Updates](https://pyup.io/repos/github/bnbalsamo/rest_demo_api/shield.svg)](https://pyup.io/repos/github/bnbalsamo/rest_demo_api/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

A demo API for use with an APIs/REST presentation.

# Installation
- ```$ git clone https://github.com/bnbalsamo/rest_demo_api.git```
- ```$ cd rest_demo_api```
- (Optional) Make any required changes to ```requirements.txt```
    - Note: Unpinning or changing dependency versions may effect functionality
- ```$ pip install -r requirements.txt```
- ```$ python setup.py install```

# Development
## Running Tests
```
$ pip install -r requirements/requirements_tests.txt
$ tox
```
Note: Tox will run tests against the version of the software installed via ```python setup.py install```.
To test against pinned dependencies add ```-r requirements.txt``` to the deps array of the tox.ini testenv
section.

## Updating Dependencies
- ```pip install -r requirements/requirements_dev.txt```
- Review ```requirements/requirements_loose.txt```
- ```tox -e pindeps```
- ```cp .tox/requirements.txt .```
- Copy pinned requirements into ```setup.py```

# Author
Brian Balsamo <Brian@BrianBalsamo.com>
