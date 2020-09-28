from .base import BaseProvider
from tfworker import constants as const


class GoogleProvider(BaseProvider):
    tag = "google"

    def __init__(self, body, authenticators, *args, **kwargs):
        super(GoogleProvider, self).__init__(body, state)

        self._authenticator = self.select_authenticator(authenticators)
        self.project = state.args.gcp_project or None
        self.creds_path = state.args.gcp_creds_path or None
        self.region = state.args.gcp_region or None
        self.gcp_prefix = None

        obj.clean = clean
        obj.add_arg("terraform_bin", kwargs.get("terraform_bin"))

        obj.add_arg("s3_bucket", kwargs.get("s3_bucket"))
        obj.add_arg("s3_prefix", s3_prefix)

        # configuration for AWS interactions
        _aws_config = z.providers["aws"].get_aws_config(deployment)
