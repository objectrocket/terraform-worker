from tfworker.commands.base import BaseCommand


class CleanCommand(BaseCommand):
    def __init__(self, rootc, *args, **kwargs):
        self._config = rootc.config
        self._deployment = kwargs.get("deployment")
        self._limit = kwargs.get("limit", [])
        super(CleanCommand, self).__init__(rootc, **kwargs)

    def exec(self):
        for prov in self._providers:
            prov.clean(self._deployment, self._limit, self._config)
