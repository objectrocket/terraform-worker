import json


class BaseProvider:
    tag = None

    def __init__(self, body):
        self.vars = body.get("vars", {})
        self.version = self.vars.get("version")

    def tfjson(self):
        return json.dumps(
            {"provider": {self.tag: self.vars}},
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
        )


class UnknownProvider(Exception):
    def __init__(self, provider):
        super().__init__(f"{provider} is not a known value.")


class BackendError(Exception):
    pass


def validate_backend_empty(state):
    """
    validate_backend_empty ensures that the provided state file
    is empty
    """

    try:
        if len(state["resources"]) > 0:
            return False
        else:
            return True
    except KeyError:
        raise BackendError("resources key does not exist in state!")


def validate_backend_region(state):
    """
    validate_backend_region validates that a statefile
    was previously used in the region the current
    deployment is being created for
    """
