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

    def hcl(self):
        result = []
        provider_vars = {}
        try:
            for k, v in self.vars.items():
                provider_vars[k] = v
        except (KeyError, TypeError):
            """No provider vars were set."""
            pass

        result.append('provider "{}" {{'.format(self.tag))
        for k, v in provider_vars.items():
            if '"' not in v:
                result.append('  {} = "{}"'.format(k, v))
            else:
                result.append("  {} = {}".format(k, v))
        result.append("}")
        return "\n".join(result)


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
