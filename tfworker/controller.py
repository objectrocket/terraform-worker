import collections
import copy
import os
import shutil
import sys

from pathlib import Path

import click
import jinja2

from tfworker.authenticators import AuthenticatorsCollection
from tfworker.backends import select_backend
from tfworker.definitions import DefinitionsCollection
from tfworker.plugins import PluginsCollection
from tfworker.providers import ProvidersCollection


class TerraformController:
    def __init__(self, state, *args, **kwargs):
        click.secho(f"kwargs: {kwargs}", fg="yellow")
        self._version = None
        self._providers = None
        self._definitions = None
        self._backend = None
        self._plugins = None
        self._tf_apply = kwargs.get("tf_apply")
        self._destroy = kwargs.get("destroy")
        self._limit = kwargs.get("limit")
        self._temp_dir = state.temp_dir
        self._repository_path = state.args.repository_path
        self._authenticators = AuthenticatorsCollection(state)

        self._plan_for = "destroy" if self._destroy else "apply"
        if self._limit:
            click.secho(f"we got limit: {self._limit}", fg="yellow")

        click.secho("loading config file {}".format(state.args.config_file), fg="green")
        state.load_config(state.args.config_file)

        self.parse_config(state.config["terraform"])

        # TODO??
        if not self._backend:
            self._backend = select_backend(state.args.backend, self._authenticators)

        if self._tf_apply and self._destroy:
            click.secho("can not apply and destroy at the same time", fg="red")
            raise SystemExit(1)

    def parse_config(self, tf):
        for k, v in tf.items():
            if k == "providers":
                self._providers = ProvidersCollection(v, self._authenticators)
            elif k == "definitions":
                self._definitions = DefinitionsCollection(
                    v, self._plan_for, self._limit
                )
            elif k == "backend":
                self._backend = select_backend(v, self._authenticators)
            elif k == "plugins":
                self._plugins = PluginsCollection(v, self.temp_dir)

    @property
    def providers(self):
        return self._providers

    @property
    def definitions(self):
        return self._definitions

    @property
    def plugins(self):
        return self._plugins

    @property
    def temp_dir(self):
        return self._temp_dir

    def prep_modules(self):
        """Puts the modules sub directories into place."""
        mod_source = "{}/terraform-modules".format(self._repository_path).replace(
            "//", "/"
        )
        mod_destination = "{}/terraform-modules".format(self._temp_dir).replace(
            "//", "/"
        )
        click.secho(
            f"copying modules from {mod_source} to {mod_destination}", fg="yellow"
        )
        shutil.copytree(
            mod_source,
            mod_destination,
            symlinks=True,
            ignore=shutil.ignore_patterns("test", ".terraform", "terraform.tfstate*"),
        )

    def exec(self):
        for definition in self.definitions:
            # execute = False
            # copy definition files / templates etc.
            click.secho("preparing definition: {}".format(definition.tag), fg="green")
            self._prep_def(definition)
            _ = """
            # run terraform init
            try:
                tf.run(
                    name,
                    obj.temp_dir,
                    terraform_bin,
                    "init",
                    key_id=_aws_config.key_id,
                    key_secret=_aws_config.key_secret,
                    key_token=_aws_config.session_token,
                    debug=show_output,
                )
            except tf.TerraformError:
                click.secho("error running terraform init", fg="red")
                raise SystemExit(1)

            click.secho("planning definition: {}".format(name), fg="green")

            # run terraform plan
            try:
                tf.run(
                    name,
                    obj.temp_dir,
                    terraform_bin,
                    "plan",
                    key_id=_aws_config.key_id,
                    key_secret=_aws_config.key_secret,
                    key_token=_aws_config.session_token,
                    debug=show_output,
                    plan_action=plan_for,
                    b64_encode=b64_encode,
                )
            except tf.PlanChange:
                execute = True
            except tf.TerraformError:
                click.secho(
                    "error planning terraform definition: {}!".format(name), fg="red"
                )
                raise SystemExit(1)

            if force_apply:
                execute = True

            if execute and tf_apply:
                if force_apply:
                    click.secho(
                        "force apply for {}, applying".format(name), fg="yellow"
                    )
                else:
                    click.secho(
                        "plan changes for {}, applying".format(name), fg="yellow"
                    )
            elif execute and destroy:
                click.secho("plan changes for {}, destroying".format(name), fg="yellow")
            elif not execute:
                click.secho("no plan changes for {}".format(name), fg="yellow")
                continue

            try:
                tf.run(
                    name,
                    obj.temp_dir,
                    terraform_bin,
                    plan_for,
                    key_id=_aws_config.key_id,
                    key_secret=_aws_config.key_secret,
                    key_token=_aws_config.session_token,
                    debug=show_output,
                    b64_encode=b64_encode,
                )
            except tf.TerraformError:
                click.secho(
                    "error with terraform {} on definition {}, exiting".format(
                        plan_for, name
                    ),
                    fg="red",
                )
                raise SystemExit(1)
            else:
                click.secho(
                    "terraform {} complete for {}".format(plan_for, name), fg="green"
                )"""

    def _prep_def(self, definition, all_defs, temp_dir, repo_path, deployment, args):
        """ prepare the definitions for running """
        repo = Path("{}/{}".format(repo_path, definition["path"]).replace("//", "/"))
        target = Path("{}/definitions/{}".format(temp_dir, name).replace("//", "/"))
        target.mkdir(parents=True, exist_ok=True)

        if not repo.exists():
            click.secho(
                "Error preparing definition {}, path {} does not exist".format(
                    name, repo.resolve()
                ),
                fg="red",
            )
            sys.exit(1)

        # Prepare variables
        terraform_vars = None
        template_vars = make_vars("template_vars", definition, all_defs)
        terraform_vars = make_vars("terraform_vars", definition, all_defs)
        locals_vars = make_vars("remote_vars", definition)
        template_vars["deployment"] = deployment
        terraform_vars["deployment"] = deployment

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
            contents = env.get_template(str(j2)).render(**template_vars)
            with open("{}/{}".format(str(target), str(j2)), "w+") as j2_file:
                j2_file.write(contents)

        # Create local vars from remote data sources
        if len(list(locals_vars.keys())) > 0:
            with open(
                "{}/{}".format(str(target), "worker-locals.tf"), "w+"
            ) as tflocals:
                tflocals.write("locals {\n")
                for k, v in locals_vars.items():
                    tflocals.write(
                        '  {} = "${{data.terraform_remote_state.{}}}"\n'.format(k, v)
                    )
                tflocals.write("}\n\n")

        # Create the terraform configuration, terraform.tf
        state = render_backend(name, deployment, args)
        remote_data = render_backend_data_source(all_defs["definitions"], name, args)
        providers = render_providers(all_defs["providers"], args)

        with open("{}/{}".format(str(target), "terraform.tf"), "w+") as tffile:
            tffile.write("{}\n\n".format(providers))
            tffile.write("{}\n\n".format(state))
            tffile.write("{}\n\n".format(remote_data))

        # Create the variable definitions
        with open("{}/{}".format(str(target), "worker.auto.tfvars"), "w+") as varfile:
            for k, v in terraform_vars.items():
                if isinstance(v, list):
                    varstring = "[{}]".format(", ".join(map(quote_str, v)))
                    varfile.write("{} = {}\n".format(k, varstring))
                else:
                    varfile.write('{} = "{}"\n'.format(k, v))
