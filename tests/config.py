"""Config for tests."""

class RemoteConfig(object):
    """Config for remote testing."""
    STORAGE_PROVIDER = "S3"
    STORAGE_KEY = ""
    STORAGE_SECRET = ""
    STORAGE_CONTAINER = "yoredis.com"
    STORAGE_ALLOWED_EXTENSIONS = []


class LocalConfig(object):
    """Config for local testing."""
    STORAGE_KEY = ""
    STORAGE_SECRET = ""
    STORAGE_PROVIDER = "LOCAL"
    STORAGE_CONTAINER = 'container_1'
    STORAGE_ALLOWED_EXTENSIONS = []
