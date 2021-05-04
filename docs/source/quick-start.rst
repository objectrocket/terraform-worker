Quick Start
===========

``terraform-worker`` is a command line tool for pipelining terraform operations while sharing state between them.
The worker consumese a yaml configuration file which is broken up into two sections, definitions (which were really
just top level modules) and sub-modules. The definitions are put into a worker config in order, with the terraform
variables, and remote state variables.

Following is a sample configuration file and command:

**TBD: Actual working example that a user can run**

Sample terraform-worker configuration: **./worker.yaml**

.. code-block:: yaml
    :linenos:

    terraform:
      providers:
        aws:
          vars:
            region: {{ aws_region }}
            version: "~> 2.61"

      # global level variables
      terraform_vars:
        region: {{ aws_region }}
        environment: dev

      definitions:
        # Either setup a VPC and resources, or deploy into an existing one
        network:
          path: /definitions/aws/network-existing

        database:
          path: git@github.com:objectrocket/tfworker-getting-started.git


.. code-block:: sh

    % worker --aws-profile default --backend s3 terraform --show-output example1
