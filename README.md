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

**NOTE:** By default, terraform-worker emits all of the providers from the configuration in each
definition's terraform.tf file.  If all of the providers are available from the default hashicorp
namespaced, this behavior is fine.  However, when using a provider from a non-hashicorp namespace
AND terraform 0.13+, definitions which do not explicitly define the `source` for the non-hashicorp
provider will not be able to resolve the provider. As a stop-gap fix, support for a `provider_excludes`
field has been added.  In the future, the terraform-worker will support auto-discovering each
definitions `required_providers`.


**provider_excludes** example:
```yaml
  providers:
    'null':
      vars:
        version: "~> 2.1"
    kubectl:
      vars:
        version: "~> 1.9"
        source: "gavinbunney/kubectl"

  definitions:
    # Either setup a VPC and resources, or deploy into an existing one
    network:
      path: /definitions/aws/network-existing

    database:
      path: /definitions/aws/rds

      provider_excludes:
        - kubectl
```


## Development

```sh
 # virtualenv setup stuff... and then:
 % pip install poetry && make init
```

## Releasing

Publishing a release to PYPI is done locally through poetry. Instructions on how to configure credentials for poetry can be found [here](https://python-poetry.org/docs/repositories/#configuring-credentials).

Bump the version of the worker and commit the change:
```sh
 % poetry version <semver_version_number>
```

Build and publish the package to PYPI:
```sh
 % poetry publish --build
```

## Configuration

A project is configured through a worker config, a yaml file that specifies the definitions, inputs, outputs, providers and all other necessary configuration. The worker config is what specifies how state is shared among your definitions. The config support jinja templating that can be used to conditionally pass state or pass in env variables through the command line via the `--config-var` option.

*./worker.yaml*
```yaml
terraform:
  providers:
    aws:
      vars:
        region: {{ aws-region }}
        version: "~> 2.61"

  # global level variables
  terraform_vars:
    region: {{ aws-region }}
    environment: dev

  definitions:
    # Either setup a VPC and resources, or deploy into an existing one
    network:
      path: /definitions/aws/network-existing

    database:
      path: /definitions/aws/rds
      remote_vars:
        subnet: network.outputs.subnet_id
```

In this config, the worker manages two separate terraform modules, a `network` and a `database` definition, and shares an output from the network definition with the database definition. This is made available inside of the `database` definition through the `local.subnet` value.

`aws-region` is substituted at runtime for the value of `--aws-region` passed through the command line.

## Troubleshooting

Running the worker with the `--no-clean` option will keep around the terraform files that the worker generates. You can use these generated files to directly run terraform commands for that definition. This is useful for when you need to do things like troubleshoot or delete items from the remote state. After running the worker with --no-clean, cd into the definition directory where the terraform-worker generates it's tf files. The worker should tell you where it's putting these for example:

```
...
building deployment mfaitest
using temporary Directory: /tmp/tmpew44uopp
...
```

In order to troubleshoot this definition, you would cd /tmp/tmpew44uopp/definitions/my_definition/ and then perform any terraform commands from there.

## Background

The terraform worker was a weekend project to run terraform against a series of definitions (modules). The idea was the configuration vars, provider configuration, remote state, and variables from remote state would all be dynamically generated. The purpose was for building kubernetes deployments, and allowing all of the configuration information to be stored as either yamnl files in github, or have the worker configuration generated by an API which stored all of the deployment configurations in a database.
