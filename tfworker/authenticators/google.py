# Copyright 2020 Richard Maynard (richard.maynard@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from tfworker import constants as const

from .base import BaseAuthenticator


class GoogleAuthenticator(BaseAuthenticator):
    tag = "google"

    def __init__(self, state_args, **kwargs):
        super(GoogleAuthenticator, self).__init__(state_args, **kwargs)

        self.bucket = self._resolve_arg("backend_bucket")
        self.creds_path = self._resolve_arg("gcp_creds_path")
        self.deployment = self._resolve_arg("deployment")
        self.prefix = self._resolve_arg("backend_prefix")
        self.project = self._resolve_arg("gcp_project")
        self.region = self._resolve_arg("gcp_region")

        if self.prefix == const.DEFAULT_BACKEND_PREFIX:
            self.gcp_prefix = const.DEFAULT_BACKEND_PREFIX.format(
                deployment=self.deployment
            )
