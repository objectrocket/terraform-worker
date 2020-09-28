import collections
import copy

import boto3
import click

from tfworker.providers import AWSProvider, GoogleProvider, UnknownProvider
from tfworker.providers import ALL as provs
from tfworker.authenticators import ALL as auths
from tfworker.backends import select_backend


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


class ProvidersCollection(collections.abc.Mapping):
    def __init__(self, providers, state):
        provider_map = dict([(prov.tag, prov) for prov in provs])
        self._providers = copy.deepcopy(providers)
        for k, v in self._providers.items():
            try:
                self._providers[k] = provider_map[k](v, state)

            except KeyError:
                raise UnknownProvider(k)

    def __len__(self):
        return len(self._providers)

    def __getitem__(self, value):
        if type(value) == int:
            return self._providers[list(self._providers.keys())[value]]
        return self._providers[value]

    def __iter__(self):
        return iter(self._providers.values())


class DefinitionsCollection(collections.abc.Mapping):
    def __init__(self, definitions, state):
        self._definitions = copy.deepcopy(definitions)
        for definition, body in self._definitions.items():
            self._definitions[definition] = Definition(definition, body)

    def __len__(self):
        return len(self._definitions)

    def __getitem__(self, value):
        if type(value) == int:
            return self._definitions[list(self._definitions.keys())[value]]
        return self._definitions[value]

    def __iter__(self):
        return iter(self._definitions.values())


class AuthenticatorsCollection(collections.abc.Mapping):
    def __init__(self, state):
        self._authenticators = dict([(auth.tag, auth(state.args)) for auth in auths])

    def __len__(self):
        return len(self._authenticators)

    def __getitem__(self, value):
        if type(value) == int:
            return self._authenticators[list(self._authenticators.keys())[value]]
        return self._authenticators[value]

    def __iter__(self):
        return iter(self._authenticators.values())


class TerraformController:
    def __init__(self, state, *args, **kwargs):
        self._version = None
        self._providers = None
        self._definitions = None
        self._plan_for = "apply"
        self._authenticators = AuthenticatorsCollection(state)

        click.secho("loading config file {}".format(state.args.config_file), fg="green")
        state.load_config(state.args.config_file)

        self.parse_config(state)

        if kwargs.get("tf_apply") and kwargs.get("destroy"):
            click.secho("can not apply and destroy at the same time", fg="red")
            raise SystemExit(1)

    def parse_config(self, state):
        for k, v in state.config["terraform"].items():
            if k == "providers":
                self._providers = ProvidersCollection(v, self._authenticators)
            elif k == "definitions":
                self._definitions = DefinitionsCollection(v, state)
            elif k == "backend":
                self._backend = select_backend(v, self._authenticators)

    @property
    def providers(self):
        return self._providers

    @property
    def definitions(self):
        return self._definitions
