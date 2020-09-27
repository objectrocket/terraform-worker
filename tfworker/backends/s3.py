import boto3
import click

from .base import BaseBackend, Backends


class S3Backend(BaseBackend):
    def __init__(self, state, *args, **kwargs):
        self.backend_region = None
        self.backend_prefix = None

        # Create locking table for aws backend
        if state.args.backend == Backends.s3:
            self.create_table(
                "terraform-{}".format(kwargs.get("deployment")),
                _aws_config.backend_region,
                _aws_config.key_id,
                _aws_config.key_secret,
                _aws_config.session_token,
            )

    @staticmethod
    def create_table(
        name,
        region,
        key_id,
        key_secret,
        session_token,
        read_capacity=1,
        write_capacity=1,
    ):
        """Create a dynamodb table."""
        client = boto3.client(
            "dynamodb",
            region_name=region,
            aws_access_key_id=key_id,
            aws_secret_access_key=key_secret,
            aws_session_token=session_token,
        )
        tables = client.list_tables()
        table_key = "LockID"
        if name in tables["TableNames"]:
            click.secho("DynamoDB lock table found, continuing.", fg="yellow")
        else:
            click.secho(
                "DynamoDB lock table not found, creating, please wait...", fg="yellow"
            )
            client.create_table(
                TableName=name,
                KeySchema=[{"AttributeName": table_key, "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": table_key, "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": read_capacity,
                    "WriteCapacityUnits": write_capacity,
                },
            )

            client.get_waiter("table_exists").wait(
                TableName=name, WaiterConfig={"Delay": 10, "MaxAttempts": 30}
            )
