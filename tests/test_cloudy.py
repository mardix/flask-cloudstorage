import os
from os.path import join, dirname
import pytest
from tests.config import LocalConfig as config
from flask_cloudy import (InvalidExtensionError, Object, get_driver_class,
                          get_file_extension, get_file_extension_type,
                          get_file_name, get_provider_name)
from libcloud.storage.base import Container, StorageDriver

CWD = dirname(__file__)

CONTAINER = "%s/%s" % (
    CWD, config.STORAGE_CONTAINER
) if config.STORAGE_PROVIDER == "LOCAL" else config.STORAGE_CONTAINER


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

    def test_empty_storage_object_evaluates_false(self, storage):
        """Check that storage object eval false if they are empty."""
        object_name = "hello.txt"
        o = storage.create(object_name)
        if o:
            raise ValueError("Object evaluated to false")

    def test_storage_object_evaluates_true(self, storage, temp_txt_file):
        """Check that storage object eval true if they are not empty."""
        o = storage.upload(temp_txt_file.name)
        o1 = storage.get(o.name)
        if not o:
            raise ValueError("Storage upload object evaluated to false")
        if not o1:
            raise ValueError("Storage get object evaluated to false")

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

    def test_storage_upload_invalid(self, storage, temp_js_file):
        """Check .js extensions are not allowed by default."""
        object_name = "my-js/hello.js"
        with pytest.raises(InvalidExtensionError):
            storage.upload(temp_js_file.name, name=object_name)

    def test_storage_upload_overwrite(self, storage, temp_txt_file,
                                      temp_js_file):
        object_name = "hello.txt"
        o = storage.upload(temp_js_file.name,
                           name=object_name,
                           overwrite=True,
                           allowed_extensions=["js"])
        o_ow = storage.upload(temp_txt_file.name,
                              name=object_name,
                              overwrite=True)
        assert isinstance(o_ow, Object)
        assert o_ow.name == o.name
        assert o_ow.name == object_name

    def test_storage_upload_no_overwrite(self, storage, temp_txt_file,
                                         temp_js_file):
        object_name = "hello.txt"
        o = storage.upload(temp_js_file.name,
                           overwrite=True,
                           allowed_extensions=["js"])
        o_no_ow = storage.upload(temp_txt_file.name,
                                 name=object_name,
                                 overwrite=False)
        assert isinstance(o_no_ow, Object)
        assert o.name != o_no_ow.name

    def test_storage_get(self, storage, temp_txt_file):
        object_name = "test_storage_get.txt"
        o = storage.upload(temp_txt_file.name,
                           name=object_name,
                           overwrite=True)
        o2 = storage.get(o.name)
        assert isinstance(o2, Object)

    def test_storage_get_none(self, storage):
        o2 = storage.get("idonexist")
        assert o2 is None

    def test_storage_upload(self, storage, temp_txt_file):
        object_name = "test_storage_upload.txt"
        storage.upload(temp_txt_file.name, name=object_name)
        o = storage.upload(temp_txt_file.name, name=object_name)
        assert isinstance(o, Object)
        assert o.name != object_name

    def test_storage_upload_use_filename_name(self, storage, temp_js_file):
        """Check that uploaded files retain thier name."""
        object_name = os.path.basename(temp_js_file.name)
        o = storage.upload(temp_js_file.name,
                           overwrite=True,
                           allowed_extensions=["js"])
        assert o.name == object_name

    def test_storage_upload_append_extension(self, storage, temp_txt_file):
        """Check that uploaded names get an appended extension."""
        object_name = "test_storage_upload_append_extension"
        o = storage.upload(temp_txt_file.name, object_name, overwrite=True)
        assert get_file_extension(o.name) == "txt"

    def test_storage_upload_with_prefix(self, storage, temp_txt_file):
        object_name = os.path.splitext(os.path.basename(temp_txt_file.name))[0]
        prefix = "dir1/dir2/dir3/"
        full_name = "%s%s.%s" % (prefix, object_name, "txt")
        o = storage.upload(temp_txt_file.name,
                           name=object_name,
                           prefix=prefix,
                           overwrite=True)
        assert full_name in storage
        assert o.name == full_name

    def test_save_to(self, storage, temp_dir, temp_txt_file):
        object_name = "test_save_to.txt"
        o = storage.upload(temp_txt_file.name, name=object_name)
        file = o.save_to(temp_dir, overwrite=True)
        file2 = o.save_to(
            temp_dir,
            name="my_new_file",
            overwrite=True)
        assert os.path.isfile(file)
        assert file2 == join(temp_dir, "my_new_file.txt")

    def test_local_server(self, storage, temp_txt_file):
        """Test the local server function."""
        object_name = "test_local_server.txt"
        storage.upload(temp_txt_file.name, name=object_name, overwrite=True)
        file_server = storage.app.view_functions['FLASK_CLOUDY_SERVER']
        response = file_server(object_name)
        assert response.status_code == 200

    @pytest.mark.timeout(30)
    def test_werkzeug_upload(self, storage, temp_png_file):
        try:
            import werkzeug
        except ImportError:
            return
        object_name = "test-werkzeug-upload.txt"
        file = werkzeug.datastructures.FileStorage(temp_png_file)
        file.filename = object_name
        o = storage.upload(file, overwrite=True)
        assert isinstance(o, Object)
        assert o.name == object_name
