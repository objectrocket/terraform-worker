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

import collections
import copy
import os
import shutil
import sys
from pathlib import Path

import click
import jinja2


class Definition:
    def __init__(
        self,
        definition,
        body,
        deployment,
        global_remote_vars,
        global_template_vars,
        global_terraform_vars,
        providers,
        repository_path,
        temp_dir,
    ):
        self.tag = definition
        self._body = body
        self._path = body.get("path")
        self._remote_vars = self.make_vars(
            body.get("remote_vars", collections.OrderedDict()), global_remote_vars
        )
        self._template_vars = self.make_vars(
            body.get("template_vars", collections.OrderedDict()), global_template_vars
        )
        self._terraform_vars = self.make_vars(
            body.get("terraform_vars", collections.OrderedDict()), global_terraform_vars
        )

        self._deployment = deployment
        self._repository_path = repository_path
        self._providers = providers
        self._temp_dir = temp_dir

    @property
    def body(self):
        return self._body

    @property
    def path(self):
        return self._path

    def prep(self, backend):
        """ prepare the definitions for running """
        repo = Path(f"{self._repository_path}/{self.path}".replace("//", "/"))
        target = Path(f"{self._temp_dir}/definitions/{self.tag}".replace("//", "/"))
        target.mkdir(parents=True, exist_ok=True)

        if not repo.exists():
            click.secho(
                f"Error preparing definition {self.tag}, path {repo.resolve()} does not"
                " exist",
                fg="red",
            )
            sys.exit(1)

        # Prepare variables
        self._template_vars["deployment"] = self._deployment
        self._terraform_vars["deployment"] = self._deployment

        # Put terraform files in place
        for tf in repo.glob("*.tf"):
            shutil.copy("{}".format(str(tf)), str(target))
        for tf in repo.glob("*.tfvars"):
            shutil.copy("{}".format(str(tf)), str(target))
        if os.path.isdir(str(repo) + "/templates".replace("//", "/")):
            shutil.copytree(
                "{}/templates".format(str(repo)), "{}/templates".format(str(target))
            )
        if os.path.isdir(str(repo) + "/policies".replace("//", "/")):
            shutil.copytree(
                "{}/policies".format(str(repo)), "{}/policies".format(str(target))
            )
        if os.path.isdir(str(repo) + "/scripts".replace("//", "/")):
            shutil.copytree(
                "{}/scripts".format(str(repo)), "{}/scripts".format(str(target))
            )
        if os.path.isdir(str(repo) + "/hooks".replace("//", "/")):
            shutil.copytree(
                "{}/hooks".format(str(repo)), "{}/hooks".format(str(target))
            )
        if os.path.isdir(str(repo) + "/repos".replace("//", "/")):
            shutil.copytree(
                "{}/repos".format(str(repo)), "{}/repos".format(str(target))
            )

        # Render jinja templates and put in place
        env = jinja2.Environment(loader=jinja2.FileSystemLoader)

        for j2 in repo.glob("*.j2"):
            contents = env.get_template(str(j2)).render(**self._template_vars)
            with open("{}/{}".format(str(target), str(j2)), "w+") as j2_file:
                j2_file.write(contents)

        # Create local vars from remote data sources
        if len(list(self._remote_vars.keys())) > 0:
            with open(
                "{}/{}".format(str(target), "worker-locals.tf"), "w+"
            ) as tflocals:
                tflocals.write("locals {\n")
                for k, v in self._remote_vars.items():
                    tflocals.write(
                        '  {} = "${{data.terraform_remote_state.{}}}"\n'.format(k, v)
                    )
                tflocals.write("}\n\n")

        with open("{}/{}".format(str(target), "terraform.tf"), "w+") as tffile:
            tffile.write("{}\n\n".format(self._providers.hcl()))
            tffile.write("{}\n\n".format(backend.hcl(self.tag)))
            tffile.write("{}\n\n".format(backend.data_hcl(self.tag)))

        # Create the variable definitions
        with open("{}/{}".format(str(target), "worker.auto.tfvars"), "w+") as varfile:
            for k, v in self._terraform_vars.items():
                if isinstance(v, list):
                    varstring = "[{}]".format(", ".join(map(Definition.quote_str, v)))
                    varfile.write("{} = {}\n".format(k, varstring))
                else:
                    varfile.write('{} = "{}"\n'.format(k, v))

    @staticmethod
    def quote_str(some_string):
        """Put literal quotes around a string."""
        return f'"{some_string}"'

    def make_vars(self, local_vars, global_vars):
        """Make a variables dictionary based on default vars, as well as specific vars for an item."""
        global_vars = global_vars or collections.OrderedDict()
        item_vars = copy.deepcopy(global_vars)
        for k, v in local_vars.items():
            # terraform expects variables in a specific type, so need to convert bools to a lower case true/false
            matched_type = False
            if v is True:
                item_vars[k] = "true"
                matched_type = True
            if v is False:
                item_vars[k] = "false"
                matched_type = True
            if not matched_type:
                item_vars[k] = v

        return item_vars


class DefinitionsCollection(collections.abc.Mapping):
    def __init__(
        self,
        definitions,
        deployment,
        limit,
        plan_for,
        providers,
        repository_path,
        rootc,
        temp_dir,
    ):
        self._body = definitions
        self._plan_for = plan_for
        self._definitions = collections.OrderedDict()
        for definition, body in definitions.items():
            if limit and definition not in limit:
                continue
            self._definitions[definition] = Definition(
                definition,
                body,
                deployment,
                rootc.remote_vars_odict,
                rootc.template_vars_odict,
                rootc.terraform_vars_odict,
                providers,
                repository_path,
                temp_dir,
            )

    def __len__(self):
        return len(self._definitions)

    def __getitem__(self, value):
        if type(value) == int:
            return self._definitions[list(self._definitions.keys())[value]]
        return self._definitions[value]

    def __iter__(self):
        return self.iter(honor_destroy=True)

    def iter(self, honor_destroy=False):
        if honor_destroy:
            if self._plan_for == "destroy":
                return iter(reversed(list(self._definitions.values())))
        return iter(self._definitions.values())

    @property
    def body(self):
        return self._body
