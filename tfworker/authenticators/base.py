class BaseAuthenticator:
    tag = "base"

    def __init__(self, state_args, *args, **kwargs):
        self._args = state_args
        self.clean = kwargs.get("clean")

    def _resolve_arg(self, name):
        return getattr(self._args, name) if hasattr(self._args, name) else None

    def env(self):
        return {}


class UnknownAuthenticator(Exception):
    def __init__(self, provider):
        super().__init__(f"{provider} is not a known value.")
