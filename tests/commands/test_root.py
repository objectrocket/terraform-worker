import copy
from unittest import mock

import pytest
import tfworker.commands.root
from tfworker.commands.root import get_platform, replace_vars


class TestMain:
    def test_rc_add_arg(self, rootc):
        rc = copy.deepcopy(rootc)
        rc.add_arg("a", 1)
        assert rc.args.a == 1

    def test_rc_add_args(self, rootc):
        rc = copy.deepcopy(rootc)
        rc.add_args({"a": 1, "b": "two"})
        assert rc.args.a == 1
        assert rc.args.b == "two"

    def test_rc_init(self, rootc):
        rc = tfworker.commands.root.RootCommand(args={"a": 1, "b": "two"})
        assert rc.args.a == 1
        assert rc.args.b == "two"

    def test_config_loader(self, rootc):
        expected_sections = ["providers", "terraform_vars", "definitions"]
        expected_tf_vars = {
            "vpc_cidr": "10.0.0.0/16",
            "region": "us-west-2",
            "domain": "test.domain.com",
        }
        terraform_config = rootc.config.get("terraform")
        for section in expected_sections:
            assert section in terraform_config.keys()

        for k, v in expected_tf_vars.items():
            assert terraform_config["terraform_vars"][k] == v

    @pytest.mark.parametrize(
        "var, expected",
        [
            ("//deployment//", "test-0001"),
            ("//aws-region//}}", "us-west-2"),
            ("//   aws-region //}}", "us-west-2"),
            ("//aws_region//}}", "us-west-2"),
            ("/aws_region/", "/aws_region/"),
            ("aws-region", "aws-region"),
        ],
    )
    def test_replace_vars(self, rootc, var, expected):
        assert replace_vars(var, rootc.args) == expected

    @pytest.mark.parametrize(
        "opsys, machine, mock_platform_opsys, mock_platform_machine",
        [
            ("linux", "i386", ["linux2"], ["i386"]),
            ("linux", "arm", ["Linux"], ["arm"]),
            ("linux", "amd64", ["linux"], ["x86_64"]),
            ("linux", "amd64", ["linux"], ["amd64"]),
            ("darwin", "amd64", ["darwin"], ["x86_64"]),
            ("darwin", "amd64", ["darwin"], ["amd64"]),
            ("darwin", "arm", ["darwin"], ["arm"]),
        ],
    )
    def test_get_platform(
        self, opsys, machine, mock_platform_opsys, mock_platform_machine
    ):
        with mock.patch("platform.system", side_effect=mock_platform_opsys) as mock1:
            with mock.patch(
                "platform.machine", side_effect=mock_platform_machine
            ) as mock2:
                actual_opsys, actual_machine = get_platform()
                assert opsys == actual_opsys
                assert machine == actual_machine
                mock1.assert_called_once()
                mock2.assert_called_once()
