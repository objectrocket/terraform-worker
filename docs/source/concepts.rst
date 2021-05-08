Configuration Concepts
======================

The **terraform-worker** is a terraform wrapper which emphasizes configuration simplicity for 
complex orchestrations.  The **terraform-worker** works by reading a configuration of terraform
provider, variable and module :ref:`definitions`, gathering provider plugins and remote terraform
sources, and then serially executing the terraform operations in a local temporary directory. The
**terraform-worker** supports passing orchestration values through a pipeline of terraform operations
via the `data\.terraform_remote_state <https://www.terraform.io/docs/language/state/remote-state-data.html>`_
data source. This section examines the **terraform-worker** concepts of :ref:`rendering`, :ref:`definitions`,
:ref:`terraform-vars`, :ref:`remote-vars`, and :ref:`provider-configurations`.

.. index::
   single: jinja templates

.. _rendering:

Rendering with Jinja templates
-------------------------------

**terraform-worker** configurations are pre-processed using the `Jinja <https://jinja.palletsprojects.com/en/2.11.x/>`_
templating language. This allows interpolation of values passed in from the command line.

.. note:: 

   Expansion of a variable passed in from the CLI:

   .. code-block:: yaml
      :emphasize-lines: 5

      providers:
        aws:
          vars:
            version: ">= 3.16.0"
            region: {{ aws_region }}

**terraform-worker** supports a special ``env`` object for interpolating values passed in the environment.

.. note::

   Expansion of a variable passed in from the environment:

   .. code-block:: yaml
      :emphasize-lines: 4-5

      definitions:
        blue:
          terraform_vars:
            name: {{ env.NAME_VAR|default("alpha") }}
            tag: {{ env.TAG_VAR|default("beta") }}

Pre-processing with Jinja allows for the use of conditional blocks. Conditional blocks might be keyed on a
`config-var` passed via the CLI.

.. note::

   TODO!!

   .. code-block:: yaml
      :emphasize-lines: 4-5

      definitions:
        blue:
          terraform_vars:
            name: {{ env.NAME_VAR|default("alpha") }}
            tag: {{ env.TAG_VAR|default("beta") }}

.. index::
   single: provider configurations

.. _provider-configurations:

Provider Configurations
-----------------------

A **terraform-worker** configuration must include information about the providers that are used by the
definitions. The **terraform-worker** uses this information to download all plugins locally and then
passes the local path to each terraform operation.

.. note::

   Following is a ``providers`` snippet from a configuration.

   .. code-block:: yaml
      :emphasize-lines: 2-9

      terraform:
        providers:
          aws:
            vars:
              version: ">= 3.16.0"
              region: {{ aws_region }}
          'null':
            vars:
              version: ">= 3.0.0"

Provider configurations typicallly include the version and any other variables that are required in a
``vars`` dictionary.  If the provider is supported from hashicorp registry, it is also possible to
explicitly stipulate the provider download location using a `baseURL` field in the provider dictionary.

.. note::

   Following is an example of a ``baseURL`` configuration.

   .. code-block:: yaml
      :emphasize-lines: 4

      terraform:
        providers:
          kubectl:
            baseURL: https://github.com/gavinbunney/terraform-provider-kubectl/releases/download/v1.9.4
            vars:
              version: "1.9.4"

.. index::
   single: definition

.. _definitions:

Definitions
-----------

A **terraform-worker** configuration is comprised of one or more definition statements. Conceptually, a 
**definition** may refer to either the statement in the configuration, or a collection of terraform and 
supporting files on a file system, or in a git repository. In general, these latter **definitions** are
lightweight.  They are mainly involved aggregating the parameters that will be supplied to an underlying
terraform module as inputs.

.. note:: TBD illustrative example??

.. _definition-statements:

Definition Statements
+++++++++++++++++++++

A **definition statement** is `key` in a :ref:`definitions` object in a **terraform-worker** configuration.
A **definition statement** must include a `key` which defines either a locally relative :ref:`filesystem-definition`
or a path to a git repository.

.. note:: TBD illustrative example??

.. _filesystem-definition:

Filesystem Definition - Root Terraform Module with benefits
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

A **filesystem definition** refers to a directory which includes a terraform root module.  It may also include a 
:ref:`hooks` directory and a :ref:`terraform-modules` directory.

.. note::

   Following is the directory tree of a sample definition.

   .. code-block:: bash

      definitions/new-ami
      ├── README.md
      ├── hooks
      │   ├── images
      │   │   └── image.pkr.hcl
      │   └── scripts
      │       └── setup.sh
      ├── main.tf
      └── outputs.tf

.. index::
   single: terraform-modules

.. _terraform-modules:

Terraform Modules
+++++++++++++++++

The **terraform-worker** can be made aware of terraform modules which may need to be copied into the
temporary directory where terraform operations are being executed so that relative paths resolve properly.

.. note:: TBD illustrative example??

.. index::
   single: terraform_vars

.. _terraform-vars:

Terraform Variables
-------------------

The ``terraform_vars`` field  in a **terraform-worker** configuration is used to express an input
variables or local variables for a terraform module. Values which appear in this block are passed to
the underlying terraform operation in a ``worker.auto.tfvars`` file.

.. note::

   Following is a ``terraform_vars`` snippet from a configuration.

   .. code-block:: yaml
      :emphasize-lines: 5-7

      terraform:
        ...
        definitions:
          blue:
            terraform_vars:
              name: alpha
              tag: beta
      ...

   Following is how this value appears in the terraform execution environment.

   .. code-block:: bash

      % pwd
      /tmp/fhgwjxkt/definitions/blue
      % cat worker.auto.tfvars
      name = "alpha"
      tag = "beta"

.. index::
   single: remote_vars

.. _remote-vars:

Remote Variables
----------------

A ``remote_vars`` field in a **terraform-worker** configuration is used to express input or local
variables that will be supplied from terraform's backend state store.

.. note::

   Following is a ``remote_vars`` snippet from a configuration.

   .. code-block:: yaml
      :emphasize-lines: 10,11

      ...
      terraform:
        ...
        definitions:
          tagging:
            # This definition includes an output value for tagmap
            path: /definitions/tagging

          blue:
            remote_vars:
              tags: tagging.output.tagmap
      ...

   Following is how this value appears in the terraform execution environment.

   .. code-block:: bash

      % pwd
      /tmp/tsgsdh6t/definitions/blue
      % cat worker-locals.tf
      locals {
        tags = data.terraform_remote_state.tagging.output.tagmap
      }
