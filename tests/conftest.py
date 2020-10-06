import collections
import os
from unittest import mock

import pytest
import tfworker
import tfworker.commands.base
import tfworker.commands.root
import tfworker.providers


@pytest.fixture
def rootc():
    result = tfworker.commands.root.RootCommand(
        args={
            "aws_access_key_id": "1234567890",
            "aws_secret_access_key": "1234567890",
            "aws_region": "us-west-2",
            "backend": "s3",
            "backend_region": "us-west-2",
            "backend_bucket": "test_bucket",
            "backend_prefix": "terraform/test-0001",
            "config_file": os.path.join(
                os.path.dirname(__file__), "fixtures", "test_config.yaml"
            ),
            "deployment": "test-0001",
            "gcp_creds_path": "/home/test/test-creds.json",
            "gcp_project": "test_project",
            "gcp_region": "us-west-2b",
            "repository_path": os.path.join(os.path.dirname(__file__), "fixtures"),
        }
    )
    return result


@pytest.fixture
@mock.patch("tfworker.authenticators.aws.AWSAuthenticator.session")
@mock.patch("tfworker.backends.s3.S3Backend.create_table")
def basec(create_table, session, rootc):
    return tfworker.commands.base.BaseCommand(rootc, "test-0001")


@pytest.fixture
@mock.patch("tfworker.authenticators.aws.AWSAuthenticator.session")
@mock.patch("tfworker.backends.s3.S3Backend.create_table")
def tf_cmd(create_table, session, rootc):
    return tfworker.commands.terraform.TerraformCommand(rootc, deployment="test-0001")


@pytest.fixture
def definition_odict():
    one_def = {
        "test": collections.OrderedDict(
            {
                "path": "/test",
                "remote_vars": {"a": 1, "b": "two"},
                "terraform_vars": {"c": 3, "d": "four"},
                "template_vars": {"e": 5, "f": "six"},
            }
        )
    }
    return collections.OrderedDict(one_def)
