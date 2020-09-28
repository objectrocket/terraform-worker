import collections
import glob
import os
import platform
import shutil
import urllib
import zipfile

import click


class PluginsCollection(collections.abc.Mapping):
    def __init__(self, body, temp_dir):
        self._plugins = body
        self._temp_dir = temp_dir

    def __len__(self):
        return len(self._providers)

    def __getitem__(self, value):
        if type(value) == int:
            return self._providers[list(self._providers.keys())[value]]
        return self._providers[value]

    def __iter__(self):
        return iter(self._providers.values())

    def download(self):
        """
        Download the required plugins.

        This could be further optimized to not download plugins from hashicorp,
        but rather have them in a local repository or host them in s3, and get
        them from an internal s3 endpoint so no transit charges are incurred.
        Ideally these would be stored between runs, and only downloaded if the
        versions have changed. In production try  to remove all all external
        repositories/sources from the critical path.
        """
        opsys, machine = PluginsCollection.get_platform()
        _platform = "{}_{}".format(opsys, machine)

        plugin_dir = "{}/terraform-plugins".format(self._temp_dir)
        if not os.path.isdir(plugin_dir):
            os.mkdir(plugin_dir)

        for name, details in self._plugins.items():
            # Get platform and strip 2 off linux 2.x kernels
            file_name = "terraform-provider-{}_{}_{}.zip".format(
                name, details["version"], _platform
            )
            uri = "https://releases.hashicorp.com/terraform-provider-{}/{}/{}".format(
                name, details["version"], file_name
            )
            click.secho(
                "getting plugin: {} version {} from {}".format(
                    name, details["version"], uri
                ),
                fg="yellow",
            )

            with urllib.request.urlopen(uri) as response, open(
                "{}/{}".format(plugin_dir, file_name), "wb"
            ) as plug_file:
                shutil.copyfileobj(response, plug_file)
            with zipfile.ZipFile("{}/{}".format(plugin_dir, file_name)) as zip_file:
                zip_file.extractall("{}/{}".format(plugin_dir, _platform))
            os.remove("{}/{}".format(plugin_dir, file_name))

            files = glob.glob("{}/{}/terraform-provider*".format(plugin_dir, _platform))
            for afile in files:
                os.chmod(afile, 0o755)

    @staticmethod
    def get_platform():
        """
        get_platform will return a formatted operating system / architecture
        tuple that is consistent with common distribution creation tools
        """

        # strip off "2" which only appears on old linux kernels
        opsys = platform.system().rstrip("2").lower()

        # make sure machine uses consistent format
        machine = platform.machine()
        if machine == "x86_64":
            machine = "amd64"

        return (opsys, machine)
