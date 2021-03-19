# terraform-worker

`terraform-worker` is a command line tool for pipelining terraform operations while sharing state between them. The worker consumese a yaml configuration file which is broken up into two sections, definitions (which were really just top level modules) and sub-modules. The definitions are put into a worker config in order, with the terraform variables, and remote state variables.  Following is a sample configuration file and command:

*./worker.yaml*
```yaml
terraform:
  providers:
    aws:
      vars:
        region: //aws-region//
        version: "~> 2.61"

  # global level variables
  terraform_vars:
    region: //aws-region//
    environment: dev

  definitions:
    # Either setup a VPC and resources, or deploy into an existing one
    network:
      path: /definitions/aws/network-existing

    database:
      path: /definitions/aws/rds
```

```sh
% worker --aws-profile default --backend s3 terraform --show-output example1
```

**NOTE:** When adding a provider from a non-hashicorp source, use a `source` field, as follows
(_the `source` field is only valid for terraform 13+ and is not emitted when using 12_):

```yaml
providers:
...
  kubectl:
    vars:
      version: "~> 1.9"
    source: "gavinbunney/kubectl"
```

## Development

```sh
 # virtualenv setup stuf... and then:
 % pip install poetry && make init
```

## Background

The terraform worker was a weekend project to run terraform against a series of definitions (modules). The idea was the configuration vars, provider configuration, remote state, and variables from remote state would all be dynamically generated. The purpose was for building kubernetes deployments, and allowing all of the configuration information to be stored as either yamnl files in github, or have the worker configuration generated by an API which stored all of the deployment configurations in a database.
