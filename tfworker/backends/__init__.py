from .s3 import S3Backend  # noqa
from .base import Backends
from .gcs import GCSBackend  # noqa


def select_backend(backend, authenticators):
    if backend == Backends.s3:
        return S3Backend(authenticators)
    elif backend == Backends.gcs:
        return GCSBackend(authenticators)
