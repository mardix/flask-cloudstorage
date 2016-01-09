"""Defines fixtures available to all tests."""

import pytest
from tempfile import TemporaryDirectory, NamedTemporaryFile
import os
from flask import Flask
from flask_cloudy import Storage
from tests.config import LocalConfig
import random


@pytest.yield_fixture(scope='function')
def temp_dir():
    """A temporary directory for each test."""
    with TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.yield_fixture(scope='function')
def temp_container():
    """A temporary container directory for each test."""
    with TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.yield_fixture(scope='function')
def temp_txt_file():
    """A temporary txt file with random contents for each test."""
    with NamedTemporaryFile(mode="w+", suffix=".txt") as temp_file:
        temp_file.write('%s' % random.random())
        temp_file.file.seek(0)
        yield temp_file


@pytest.yield_fixture(scope='function')
def temp_png_file():
    """A temporary txt file with random contents for each test."""
    with NamedTemporaryFile(suffix=".png") as temp_file:
        yield temp_file


@pytest.yield_fixture(scope='function')
def temp_js_file():
    """A temporary js file with random contents for each test."""
    with NamedTemporaryFile(mode="w+", suffix=".js") as temp_file:
        temp_file.write('%s' % random.random())
        temp_file.file.seek(0)
        yield temp_file


@pytest.yield_fixture(scope='function')
def app(temp_container):
    """An application for the tests."""
    app = Flask(__name__)
    LocalConfig.STORAGE_CONTAINER = temp_container
    app.config.from_object(LocalConfig)

    ctx = app.test_request_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture(scope='function')
def storage(app):
    """A flask-cloudy storage instance for tests."""
    storage = Storage(app=app)
    storage.app = app
    return storage
