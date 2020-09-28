from .s3 import S3Backend  # noqa
from .base import Backends
from .gcs import GCSBackend  # noqa


def select_backend(backend, state, controller):
    if Backends.s3 in backend:
        return S3Backend(backend, state, controller)
    elif Backends.gcs in backend:
        return GCSBackend(backend, state, controller)
