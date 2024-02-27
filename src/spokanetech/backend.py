from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzureMediaStorage(AzureStorage):
    """Azure media storage backend."""

    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = "media"
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    """Azure static storage backend."""

    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = "static"
    expiration_secs = None
