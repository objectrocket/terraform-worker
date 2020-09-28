import collections

import click


class Definition:
    tag = None

    def __init__(self, definition, body):
        self.tag = definition
        self._body = body
        self._path = body.get("path")
        self._remote_vars = body.get("remote_vars")
        self._terraform_vars = body.get("terraform_vars")

    @property
    def path(self):
        return self.path

    @property
    def remote_vars(self):
        return self._remote_vars

    @property
    def terraform_vars(self):
        return self._terraform_vars


class DefinitionsCollection(collections.abc.Mapping):
    def __init__(self, definitions, plan_for, limit):
        self._definitions = collections.OrderedDict()
        self._plan_for = plan_for
        click.secho(f"limit: {limit}", fg="yellow")
        for definition, body in definitions.items():
            if limit and definition not in limit:
                continue
            self._definitions[definition] = Definition(definition, body)

    def __len__(self):
        return len(self._definitions)

    def __getitem__(self, value):
        if type(value) == int:
            return self._definitions[list(self._definitions.keys())[value]]
        return self._definitions[value]

    def __iter__(self):
        if self._plan_for == "destroy":
            return iter(reversed(list(self._definitions.values())))
        return iter(self._definitions.values())
