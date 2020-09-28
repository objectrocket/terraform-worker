import boto3

from .base import BaseAuthenticator
from tfworker import constants as const


class AWSAuthenticator(BaseAuthenticator):
    tag = "aws"

    def __init__(self, args):
        super(AWSAuthenticator, self).__init__(args)

        self.access_key_id = self._resolve_arg("aws_access_key_id")
        self.backend_region = self._resolve_arg("backend_region")
        self.bucket = self._resolve_arg("backend_bucket")
        self.deployment = self._resolve_arg("deployment")
        self.prefix = self._resolve_arg("backend_prefix")
        self.region = self._resolve_arg("aws_region")
        self.role_arn = self._resolve_arg("role_arn")
        self.secret_access_key = self._resolve_arg("aws_secret_access_key")
        self.session_token = self._resolve_arg("aws_session_token")

        self._session = None
        self._backend_session = None

        # If the default value is used, render the deployment name into it
        if self.prefix == const.DEFAULT_BACKEND_PREFIX:
            self.prefix = const.DEFAULT_BACKEND_PREFIX.format(
                deployment=self.deployment
            )

    @property
    def session_args(self):
        args = dict()

        if self.profile:
            args["profile_name"] = self.profile

        if self.access_key_id:
            args["aws_access_key_id"] = self.access_key_id

        if self.secret_access_key:
            args["aws_secret_access_key"] = self.secret_access_key

        if self.session_token is not None:
            args["aws_session_token"] = self.session_token

        return args

    @property
    def backend_session(self):
        return self._backend_session

    @property
    def session(self):
        if not self._session:
            self._session = boto3.Session(region_name=self.region, **self.session_args)

            if not self.role_arn:
                # if a role was not provided, need to ensure credentials areset
                # in the config, these will come from the session
                self.access_key_id = self._session.get_credentials().access_key
                self.secret_access_key = self._session.get_credentials().secret_key
                self.session_token = self._session.get_credentials().token

                if self.backend_region == self.region:
                    self._backend_session = self._session
                else:
                    self._backend_session = boto3.Session(
                        region_name=self.backend_region, **self.session_args
                    )
            else:
                (self.__session, creds) = self.get_assumed_role_session(
                    self._session, self.self.role_arn
                )
                self.access_key_id = creds["AccessKeyId"]
                self.secret_access_key = creds["SecretAccessKey"]
                self.session_token = creds["SessionToken"]

                if self.backend_region == self.region:
                    self._backend_session = self._session
                else:
                    self._backend_session = boto3.Session(
                        region_name=self.backend_region,
                        aws_access_key_id=self.access_key_id,
                        aws_secret_access_key=self.secret_access_key,
                        aws_session_token=self.session_token,
                    )

        return self._session

    @staticmethod
    def get_assumed_role_session(
        session, role_arn, session_name="AssumedRoleSession1", duration=3600
    ):
        """ get_assumed_role_session returns a boto3 session updated with assumed role credentials """
        sts_client = session.client("sts")
        role_creds = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName=session_name, DurationSeconds=duration
        )["Credentials"]

        new_session = boto3.Session(
            aws_access_key_id=role_creds["AccessKeyId"],
            aws_secret_access_key=role_creds["SecretAccessKey"],
            aws_session_token=role_creds["SessionToken"],
        )

        return new_session, role_creds
