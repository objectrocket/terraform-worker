import click

from tfworker.authenticators import AuthenticatorsCollection
from tfworker.definitions import DefinitionsCollection
from tfworker.plugins import PluginsCollection
from tfworker.providers import ProvidersCollection


class BaseCommand:
    def __init__(self, rootc, *args, **kwargs):
        self._version = None
        self._providers = None
        self._definitions = None
        self._backend = None
        self._plugins = None

        self._temp_dir = rootc.temp_dir
        self._repository_path = rootc.args.repository_path
        self._authenticators = AuthenticatorsCollection(rootc)

        click.secho("loading config file {}".format(rootc.args.config_file), fg="green")
        rootc.load_config(rootc.args.config_file)

        # HACKIE HACKHACK
        click.secho(f"kwargs: {kwargs}")
        rootc.clean = kwargs.get("clean", True)

    def parse_config(self, tf):
        for k, v in tf.items():
            if k == "providers":
                self._providers = ProvidersCollection(v, self._authenticators)
            elif k == "definitions":
                self._definitions = DefinitionsCollection(
                    v,
                    self._deployment,
                    self._limit,
                    self._plan_for,
                    self._providers,
                    self._repository_path,
                    self._temp_dir,
                )
            elif k == "plugins":
                self._plugins = PluginsCollection(v, self._temp_dir)

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
