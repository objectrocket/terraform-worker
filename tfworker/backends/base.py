from .s3 import S3Backend
from .gcs import GCSBackend


class BaseBackend:
    tag = "base"


class Backends:
    s3 = "s3"
    gcs = "gcs"


def select_backend(backend, state, controller):
    if Backends.s3 in backend:
        return S3Backend(backend, state, controller)
    elif Backends.gcs in backend:
        return GCSBackend(backend, state, controller)
