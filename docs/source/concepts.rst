Concepts
========

The **terraform-worker** is a terraform wrapper which emphasizes configuration simplicity for 
complex orchestrations.  The **terraform-worker** works by reading a configuration of terraform
provider, variable and module :ref:`definitions`, gathering provider plugins and remote terraform
sources, and then serially executing the terraform operations in a local temporary directory. The 
**terraform-worker** supports passing orchestration values through a pipeline of terraform operations
via the `data\.terraform_remote_state <https://www.terraform.io/docs/language/state/remote-state-data.html>`_
data source. This section examines the **terraform-worker** concepts of :ref:`definitions`,
:ref:`terraform-vars`, :ref:`remote-vars`, and :ref:`provider-configurations`.

.. index::
   single: provider configurations

.. _provider-configurations:

Provider Configurations
-----------------------

TBD

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

Filesystem Definition
+++++++++++++++++++++

A **filesystem definition** refers to a directory which includes a terraform root module.  It may also include a 
:ref:`hooks` directory and a :ref:`terraform-modules` directory.

.. note:: TBD illustrative example??

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

      ...
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
