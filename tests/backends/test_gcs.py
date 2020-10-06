import copy

import pytest

import tfworker


@pytest.fixture
def gbasec(rootc):
    _copy = copy.deepcopy(rootc)
    _copy.args.backend = "gcs"
    _copy.args.backend_bucket = "test_gcp_bucket"
    _copy.args.backend_prefix = "terraform/test-0002"
    return tfworker.commands.base.BaseCommand(_copy, "test-0001-gcs")


def test_google_hcl(gbasec):
    render = gbasec.backend.hcl("test")
    expected_render = """terraform {
  backend "gcs" {
    bucket = "test_gcp_bucket"
    prefix = "terraform/test-0002/test"
    credentials = "/home/test/test-creds.json"
  }
}"""
    assert render == expected_render


def test_google_data_hcl(gbasec):
    render = gbasec.backend.data_hcl("test2")
    expected_render = """data "terraform_remote_state" "test" {
  backend = "gcs"
  config = {
    bucket = "test_gcp_bucket"
    prefix = "terraform/test-0002/test"
    credentials = "/home/test/test-creds.json"
  }
}"""
    assert render == expected_render
