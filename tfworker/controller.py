import collections
import copy

import boto3
import click

from tfworker.providers import AWSProvider, GoogleProvider, UnknownProvider
from tfworker.backends.base import select_backend


# TODO(jwiles): Can we get away with only having the aws_config object on the backend??


class Definition:
    tag = None

    def __init__(self, definition, body):
        self.tag = definition
        self._body = body
        self._path = body.get("path")
        self._remote_vars = body.get("remote_vars")
        self._terraform_vars = body.get("terraform_vars")

    @property
    def path(self):
        return self.path

    @property
    def remote_vars(self):
        return self._remote_vars

    @property
    def terraform_vars(self):
        return self._terraform_vars


class ProvidersCollection(collections.abc.Mapping):
    _provider_map = {"aws": AWSProvider, "google": GoogleProvider}

    def __init__(self, providers, state):
        self._providers = copy.deepcopy(providers)
        for k, v in self._providers.items():
            try:
                self._providers[k] = self._provider_map[k](v, state)

            except KeyError:
                raise UnknownProvider(k)

    def __len__(self):
        return len(self._providers)

    def __getitem__(self, value):
        if type(value) == int:
            return self._providers[list(self._providers.keys())[value]]
        return self._providers[value]

    def __iter__(self):
        return iter(self._providers.values())


class DefinitionsCollection(collections.abc.Mapping):
    def __init__(self, definitions, state):
        self._definitions = copy.deepcopy(definitions)
        for definition, body in self._definitions.items():
            self._definitions[definition] = Definition(definition, body)

    def __len__(self):
        return len(self._definitions)

    def __getitem__(self, value):
        if type(value) == int:
            return self._definitions[list(self._definitions.keys())[value]]
        return self._definitions[value]

    def __iter__(self):
        return iter(self._definitions.values())


class TerraformController:
    def __init__(self, state, *args, **kwargs):
        self._version = None
        self._providers = None
        self._definitions = None
        self._plan_for = "apply"
        self._aws_config = None

        click.secho("loading config file {}".format(state.args.config_file), fg="green")
        state.load_config(state.args.config_file)

        self.parse_config(state)

        if kwargs.get("tf_apply") and kwargs.get("destroy"):
            click.secho("can not apply and destroy at the same time", fg="red")
            raise SystemExit(1)

        self._aws_config = aws_config.create(state, kwargs.get("deployment"))

    def parse_config(self, state):
        for k, v in state.config["terraform"].items():
            if k == "providers":
                self._providers = ProvidersCollection(v, state, self)
            elif k == "definitions":
                self._definitions = DefinitionsCollection(v, state)
            elif k == "backend":
                self._backend = select_backend(v, state, self)

    @property
    def providers(self):
        return self._providers

    @property
    def definitions(self):
        return self._definitions


class aws_config(object):
    """
    aws_config provides an object to hold the required configuration needed for AWS
    provider options. This current holds extra attributes in order to expose session
    credentials to terraform.
    """

    def __init__(
        self,
        region,
        backend_region,
        deployment,
        state_bucket,
        state_prefix,
        key_id=None,
        key_secret=None,
        session_token=None,
        aws_profile=None,
        role_arn=None,
    ):
        self.__key_secret = key_secret
        self.__key_id = key_id
        self.__region = region
        self.__backend_region = backend_region
        self.__deployment = deployment
        self.__session_token = session_token
        self.__state_bucket = state_bucket
        self.__state_prefix = state_prefix

        session_args = dict()

        if aws_profile is not None:
            session_args["profile_name"] = aws_profile

        if key_id is not None:
            session_args["aws_access_key_id"] = key_id

        if key_secret is not None:
            session_args["aws_secret_access_key"] = key_secret

        if session_token is not None:
            session_args["aws_session_token"] = session_token

        # create the base boto session
        self.__session = boto3.Session(region_name=self.__region, **session_args)

        # handle cases for assuming the role, and create a session for the state region
        if role_arn is None:
            # if a role was not provided, need to ensure credentials are set in the config, these will come from the session self.__key_id = self.__session.get_credentials().access_key
            self.__key_secret = self.__session.get_credentials().secret_key
            self.__session_token = self.__session.get_credentials().token

            if backend_region == region:
                self.__state_session = self.__session
            else:
                self.__state_session = boto3.Session(
                    region_name=self.__backend_region, **session_args
                )
        else:
            (self.__session, creds) = get_assumed_role_session(self.__session, role_arn)
            self.__key_id = creds["AccessKeyId"]
            self.__key_secret = creds["SecretAccessKey"]
            self.__session_token = creds["SessionToken"]

            if backend_region == region:
                self.__state_session = self.__session
            else:
                self.__state_session = boto3.Session(
                    region_name=self.__backend_region,
                    aws_access_key_id=self.__key_id,
                    aws_secret_access_key=self.__key_secret,
                    aws_session_token=self.__session_token,
                )

    @property
    def key_secret(self):
        return self.__key_secret

    @property
    def key_id(self):
        return self.__key_id

    @property
    def session_token(self):
        return self.__session_token

    @property
    def state_bucket(self):
        return self.__state_bucket

    @property
    def state_prefix(self):
        return self.__state_prefix

    @property
    def region(self):
        return self.__region

    @property
    def backend_region(self):
        return self.__backend_region

    @property
    def deployment(self):
        return self.__deployment

    @property
    def session(self):
        return self.__session

    @property
    def state_session(self):
        return self.__state_session

    @staticmethod
    def get_aws_config(state, deployment):
        """ returns an aws_config based on the paramenters sent to CLI """
        # build params for aws_config based on inputs

        config_args = dict()
        if state.aws_access_key_id is not None:
            config_args["key_id"] = state.aws_access_key_id

        if state.aws_secret_access_key is not None:
            config_args["key_secret"] = state.aws_secret_access_key

        if state.aws_session_token is not None:
            config_args["session_token"] = state.aws_session_token

        if state.aws_profile is not None:
            config_args["aws_profile"] = state.aws_profile

        if state.aws_role_arn is not None:
            config_args["role_arn"] = state.aws_role_arn

        return aws_config(
            state.aws_region,
            state.backend_region,
            deployment,
            state.s3_bucket,
            state.s3_prefix,
            **config_args,
        )
