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
