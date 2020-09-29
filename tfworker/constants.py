import os

DEFAULT_BACKEND_BUCKET = "tfworker-terraform-states"
DEFAULT_BACKEND_PREFIX = "terraform/state/{deployment}"
DEFAULT_CONFIG = "{}/worker.yaml".format(os.getcwd())
DEFAULT_REPOSITORY_PATH = "{}".format(os.getcwd())
DEFAULT_AWS_REGION = "us-west-2"
DEFAULT_GCP_REGION = "us-west2b"
DEFAULT_BACKEND_REGION = "us-west-2"
DEFAULT_TERRFORM = "/usr/local/bin/terraform"
