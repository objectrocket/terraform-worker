from .base import BaseBackend


class GCSBackend(BaseBackend):
    def __init__(self, *args, **kwargs):
        self.backend_region = None
        self.backend_prefix = None
