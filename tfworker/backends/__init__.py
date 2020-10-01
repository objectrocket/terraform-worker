from .s3 import S3Backend  # noqa
from .base import Backends
from .gcs import GCSBackend  # noqa


def select_backend(backend, deployment, authenticators, definitions):
    if backend == Backends.s3:
        return S3Backend(authenticators, definitions, deployment=deployment)
    elif backend == Backends.gcs:
        return GCSBackend(authenticators, definitions, deployment=deployment)
