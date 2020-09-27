import os

DEFAULT_GCP_BUCKET = "tfworker-terraform-states"
DEFAULT_CONFIG = "{}/worker.yaml".format(os.getcwd())
DEFAULT_GCP_PREFIX = "terraform/state/{deployment}"
DEFAULT_REPOSITORY_PATH = "{}".format(os.getcwd())
DEFAULT_S3_BUCKET = "tfworker-terraform-states"
DEFAULT_S3_PREFIX = "terraform/state/{deployment}"
DEFAULT_AWS_REGION = "us-west-2"
DEFAULT_GCP_REGION = "us-west2b"
DEFAULT_BACKEND_REGION = "us-west-2"
DEFAULT_TERRFORM = "/usr/local/bin/terraform"
