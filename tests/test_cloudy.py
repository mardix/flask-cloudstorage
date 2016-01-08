
import os
import pytest
from tests.config import LocalConfig as config

from flask_cloudy import (InvalidExtensionError, Object, get_driver_class,
                          get_file_extension, get_file_extension_type,
                          get_file_name, get_provider_name)
from libcloud.storage.base import Container, StorageDriver

CWD = os.path.dirname(__file__)

CONTAINER = "%s/%s" % (CWD, config.STORAGE_CONTAINER) if config.STORAGE_PROVIDER == "LOCAL" else config.STORAGE_CONTAINER


class TestUtilities:
    """Test flask_cloudy utilities."""

    def test_get_file_extension(self):
        filename = "hello.jpg"
        assert get_file_extension(filename) == "jpg"

    def test_get_file_extension_type(self):
        filename = "hello.mp3"
        assert get_file_extension_type(filename) == "AUDIO"

    def test_get_file_name(self):
        filename = "/dir1/dir2/dir3/hello.jpg"
        assert get_file_name(filename) == "hello.jpg"

    def test_get_provider_name(self):
        class GoogleStorageDriver(object):
            pass
        driver = GoogleStorageDriver()
        assert get_provider_name(driver) == "google_storage"

    def test_get_driver_class(self):
        driver = get_driver_class("S3")
        assert isinstance(driver, type)


class TestLocalStorage:
    """Test local storage."""

    def test_driver(self, storage):
        assert isinstance(storage.driver, StorageDriver)

    def test_container(self, storage):
        assert isinstance(storage.container, Container)

    def test_flask_app(self, storage):
        assert isinstance(storage.driver, StorageDriver)

    def test_iter(self, storage):
        l = [o for o in storage]
        assert isinstance(l, list)

    def test_storage_object_not_exists(self, storage):
        object_name = "hello.png"
        assert object_name not in storage

    def test_storage_object(self, storage):
        object_name = "hello.txt"
        o = storage.create(object_name)
        assert isinstance(o, Object)

    def test_object_type_extension(self, storage):
        object_name = "hello.jpg"
        o = storage.create(object_name)
        assert o.type == "IMAGE"
        assert o.extension == "jpg"

    def test_object_provider_name(self, storage):
        object_name = "hello.jpg"
        o = storage.create(object_name)
        assert o.provider_name == config.STORAGE_PROVIDER.lower()

    def test_object_object_path(self, storage):
        object_name = "hello.jpg"
        o = storage.create(object_name)
        p = "%s/%s" % (o.container.name, o.name)
        assert o.path.endswith(p)

    def test_storage_upload_invalid(self, storage):
        object_name = "my-js/hello.js"
        with pytest.raises(InvalidExtensionError):
            storage.upload(CWD + "/data/hello.js", name=object_name)

    def test_storage_upload_ovewrite(self, storage):
        object_name = "my-txt-hello.txt"
        o = storage.upload(CWD + "/data/hello.txt", name=object_name, overwrite=True)
        assert isinstance(o, Object)
        assert o.name == object_name

    def test_storage_get(self, storage):
        object_name = "my-txt-helloIII.txt"
        o = storage.upload(CWD + "/data/hello.txt", name=object_name, overwrite=True)
        o2 = storage.get(o.name)
        assert isinstance(o2, Object)

    def test_storage_get_none(self, storage):
        o2 = storage.get("idonexist")
        assert o2 is None

    def test_storage_upload(self, storage):
        object_name = "my-txt-hello2.txt"
        storage.upload(CWD + "/data/hello.txt", name=object_name)
        o = storage.upload(CWD + "/data/hello.txt", name=object_name)
        assert isinstance(o, Object)
        assert o.name != object_name

    def test_storage_upload_use_filename_name(self, storage):
        object_name = "hello.js"
        o = storage.upload(CWD + "/data/hello.js", overwrite=True, allowed_extensions=["js"])
        assert o.name == object_name

    def test_storage_upload_append_extension(self, storage):
        object_name = "my-txt-hello-hello"
        o = storage.upload(CWD + "/data/hello.txt", object_name, overwrite=True)
        assert get_file_extension(o.name) == "txt"

    def test_storage_upload_with_prefix(self, storage):
        object_name = "my-txt-hello-hello"
        prefix = "dir1/dir2/dir3/"
        full_name = "%s%s.%s" % (prefix, object_name, "txt")
        o = storage.upload(CWD + "/data/hello.txt", name=object_name, prefix=prefix, overwrite=True)
        assert full_name in storage
        assert o.name == full_name

    def test_save_to(self, storage):
        object_name = "my-txt-hello-to-save.txt"
        o = storage.upload(CWD + "/data/hello.txt", name=object_name)
        file = o.save_to(CWD + "/data", overwrite=True)
        file2 = o.save_to(CWD + "/data", name="my_new_file", overwrite=True)
        assert os.path.isfile(file)
        assert file2 == CWD + "/data/my_new_file.txt"

    def test_werkzeug_upload(self, storage):
        try:
            import werkzeug
        except ImportError:
            return
        object_name = "my-txt-hello.txt"
        filepath = CWD + "/data/hello.txt"
        file = None
        with open(filepath, 'rb') as fp:
            file = werkzeug.datastructures.FileStorage(fp)
            file.filename = object_name
            o = storage.upload(file, overwrite=True)
            assert isinstance(o, Object)
            assert o.name == object_name

    def test_local_server(self, storage):
        """Test the local server function."""
        object_name = "test_local_server.txt"
        storage.upload(CWD + "/data/hello.txt", name=object_name, overwrite=True)
        file_server = storage.app.view_functions['FLASK_CLOUDY_SERVER']
        response = file_server(object_name)
        assert response.status_code == 200
