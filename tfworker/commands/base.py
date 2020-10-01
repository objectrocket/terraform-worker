from collections import OrderedDict
import click

from tfworker.authenticators import AuthenticatorsCollection
from tfworker.backends import select_backend
from tfworker.definitions import DefinitionsCollection
from tfworker.plugins import PluginsCollection
from tfworker.providers import ProvidersCollection


class BaseCommand:
    def __init__(
        self, rootc, deployment="undefined", limit=None, plan_for="apply", **kwargs
    ):
        self._version = None
        self._providers = None
        self._definitions = None
        self._backend = None
        self._plugins = None
        self._terraform_vars = OrderedDict()
        self._remote_vars = OrderedDict()
        self._local_vars = OrderedDict()

        self._temp_dir = rootc.temp_dir
        self._repository_path = rootc.args.repository_path
        click.secho(f"kwwargs: {kwargs}", fg="yellow")
        self._authenticators = AuthenticatorsCollection(
            rootc.args, deployment=deployment, **kwargs
        )

        rootc.clean = kwargs.get("clean", True)

        self._providers = ProvidersCollection(
            rootc.providers_odict, self._authenticators
        )
        self._definitions = DefinitionsCollection(
            rootc.definitions_odict,
            deployment,
            limit,
            plan_for,
            self._providers,
            self._repository_path,
            rootc,
            self._temp_dir,
        )
        self._plugins = PluginsCollection(rootc.plugins_odict, self._temp_dir)
        import pdb

        pdb.set_trace()
        self._backend = select_backend(
            rootc.args.backend, deployment, self._authenticators, self._definitions,
        )

    @property
    def providers(self):
        return self._providers

    @property
    def definitions(self):
        return self._definitions

    @property
    def plugins(self):
        return self._plugins

    @property
    def temp_dir(self):
        return self._temp_dir

    @property
    def repository_path(self):
        return self._repository_path
