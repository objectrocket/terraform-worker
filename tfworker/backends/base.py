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

import json


class BaseBackend:
    tag = "base"

    def tfjson(self):
        return json.dumps(
            {
                "provider": {
                    self.tag: {
                        "region": self._authenticator.region,
                        "prefix": self._authenticator.prefix,
                    }
                }
            },
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
        )


class Backends:
    s3 = "s3"
    gcs = "gcs"
