class BaseAuthenticator:
    tag = "base"

    def __init__(self, args):
        self._args = args

    def _resolve_arg(self, name):
        return getattr(self._args, name) if hasattr(self._args, name) else None


class UnknownAuthenticator(Exception):
    def __init__(self, provider):
        super().__init__(f"{provider} is not a known value.")
