from .base import BaseBackend


class GCSBackend(BaseBackend):
    tag = "gcs"
    auth_tag = "google"

    def __init__(self, authenticators, definitions, deployment=None):
        self._authenticator = authenticators[self.auth_tag]
        self._definitions = definitions
        if deployment:
            self._deployment = deployment

    def hcl(self, name):
        state_config = []
        state_config.append("terraform {")
        state_config.append('  backend "gcs" {')
        state_config.append(f'    bucket = "{self._authenticator.bucket}"')
        state_config.append(f'    prefix = "{self._authenticator.prefix}/{name}"')
        if self._authenticator.creds_path:
            state_config.append(f'    credentials = "{self._authenticator.creds_path}"')
        state_config.append("  }")
        state_config.append("}")
        return "\n".join(state_config)

    def data_hcl(self, exclude):
        remote_data_config = []
        # Call the iter method for explicit control of iteration order
        for definition in self._definitions.iter():
            if definition.tag == exclude:
                break
            remote_data_config.append(
                f'data "terraform_remote_state" "{definition.tag}" {{'
            )
            remote_data_config.append('  backend = "gcs"')
            remote_data_config.append("  config = {")
            remote_data_config.append(f'    bucket = "{self._authenticator.bucket}"')
            remote_data_config.append(
                f'    prefix = "{self._authenticator.prefix}/{definition.tag}"'
            )
            if self._authenticator.creds_path:
                remote_data_config.append(
                    f'    credentials = "{self._authenticator.creds_path}"'
                )
            remote_data_config.append("  }")
            remote_data_config.append("}")
        return "\n".join(remote_data_config)
