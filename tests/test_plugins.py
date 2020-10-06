import glob
import os

import tfworker.commands.root
import tfworker.plugins


class TestPlugins:
    def test_plugin_download(self, rootc):
        opsys, machine = tfworker.commands.root.get_platform()
        plugins = tfworker.plugins.PluginsCollection(
            {"null": {"version": "2.1.2"}}, rootc.temp_dir
        )
        plugins.download()
        files = glob.glob(
            "{}/terraform-plugins/{}_{}/terraform-provider-null_v2.1.2*".format(
                rootc.temp_dir, opsys, machine
            )
        )
        assert len(files) > 0
        for afile in files:
            assert os.path.isfile(afile)
            assert (os.stat(afile).st_mode & 0o777) == 0o755
