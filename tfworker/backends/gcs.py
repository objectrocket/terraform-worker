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

import io
import json
import os
import re

from .base import BaseBackend

from google.cloud import storage

REGION_REGEX = r'tag[0-9]+-[0-9]+-[0-9]+(-rc[0-9]+)?-(.+)-kubeflow'


def region_from_kubeflow_gcp_state(state):
    try:
        for resource in state['resources']:
            if resource['type'] == 'google_storage_bucket':
                for instance in resource['instances']:
                    return instance['attributes']['location'].lower()
    except KeyError:
        pass
    return None


def region_from_iap_config_state(state):
    try:
        for resource in state['resources']:
            if resource['type'] == 'terraform_remote_state':
                for instance in resource['instances']:
                    bucket = instance['attributes']['outputs']['value']['default_pipelines_bucket']
                    m = re.search(REGION_REGEX, bucket)
                    if m is not None:
                        return m.group(2)
    except KeyError:
        pass
    return None


def region_from_network_state(state):
    try:
        for resource in state['resources']:
            if resource['type'] == 'terraform_remote_state':
                for instance in resource['instances']:
                    try:
                        bucket = instance['attributes']['outputs']['value']['default_pipelines_bucket']
                        m = re.search(REGION_REGEX, bucket)
                        if m is not None:
                            return m.group(2)
                    except KeyError:
                        continue
    except KeyError:
        pass
    return None


def region_from_kubeflow_charts(state):
    try:
        for resource in state['resources']:
            if resource['type'] == 'google_compute_zones':
                for instance in resource['instances']:
                    return instance['attributes']['region'].lower()
    except KeyError:
        pass
    return None


state_extractors = {
    'network': region_from_network_state,
    'iap_config': region_from_iap_config_state,
    'kubeflow_gcp': region_from_kubeflow_gcp_state,
    'kubeflow_charts': region_from_kubeflow_charts,
}


class GCSBackend(BaseBackend):
    tag = "gcs"
    auth_tag = "google"

    def __init__(self, authenticators, definitions, deployment=None):
        self._authenticator = authenticators[self.auth_tag]
        self._definitions = definitions
        if deployment:
            self._deployment = deployment

    def ensure_correct_region(self):
        os.environ.update(self._authenticator.env())
        prefix = f'{self._authenticator.prefix}/'
        client = storage.Client()
        bucket = client.get_bucket(self._authenticator.bucket)
        blobs = list(client.list_blobs(bucket, prefix=prefix))
        state_region = None
        for blob in blobs:
            if not blob.name.endswith(".tfstate"):
                continue
            definition = blob.name.split('/')[-2]
            if definition in state_extractors:
                text = io.BytesIO()
                client.download_blob_to_file(blob, text)
                text.seek(0)
                state_region = state_extractors[definition](json.load(text))
                if state_region is not None:
                    break

        if state_region != self._authenticator.region:
            raise ValueError(f'Region {self._authenticator.region} does not match state region {state_region}')
        return

    def hcl(self, name):
        state_config = []
        state_config.append('  backend "gcs" {')
        state_config.append(f'    bucket = "{self._authenticator.bucket}"')
        state_config.append(f'    prefix = "{self._authenticator.prefix}/{name}"')
        if self._authenticator.creds_path:
            state_config.append(f'    credentials = "{self._authenticator.creds_path}"')
        state_config.append("  }")
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
