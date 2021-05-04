Commands
========

This section provides an explanation of the **version**, **terraform**, and **clean** commands
to the ``terraform-worker``.

.. contents:: On this page
   :depth: 3

version
-------

.. index::
   pair: commands; version

The **version** command provides the semantic version information for the ``terraform-worker``.

.. code-block:: bash

   % worker version
   terraform-worker version 0.10.1

terraform
---------

.. index::
   pair: commands; terraform

The **terraform** command is used to initialize the terraform definition calls expressed in the
configuration.  The **terraform** command supports the following arguments.

\-\-clean / \-\-no-clean
++++++++++++++++++++++++

.. index::
   triple: terraform; options; --no-clean
.. index::
   triple: terraform; options; --clean

The **--no-clean** flag will prevent the temporary directory where terraform operations are executed
from being deleted when the ``terraform-worker`` command completes.  The **--clean** option will cause
the temporary directory to be deleted.  By default, the **--clean** option is active.

\-\-apply / \-\-no-apply
++++++++++++++++++++++++

.. index::
   triple: terraform; options; --no-apply
.. index::
   triple: terraform; options; --apply

The **--no-apply** flag will cause the operations for each terraform definition to only execute
``terraform plan``.  The **--apply** flag will cause ``terraform apply`` to be executed.  By default,
the **--no-apply** option is active.

\-\-force / \-\-no-force
++++++++++++++++++++++++

.. index::
   triple: terraform; options; --no-force
.. index::
   triple: terraform; options; --force

The **--no-force** flag will omit the ``-force`` option from a ``terraform apply`` or ``terraform destroy`` operation.
``terraform plan``.  The **--force** flag will cause the ``-force`` option to be included in ``terraform apply`` and 
``terraform destory`` operations.

\-\-destroy / \-\-no-destroy
++++++++++++++++++++++++++++

.. index::
   triple: terraform command; options; --no-destroy
.. index::
   triple: terraform command; options; --destroy

The **--no-destroy** flag will prevent each terraform definition from executing ``terraform destroy``.  The **--destroy**
flag will cause ``terraform destroy`` to be executed. ``destroy`` will only be called when ``--destroy`` is passed, so
``--no-destroy`` has no effect.

\-\-show-output / \-\-no-show-output
++++++++++++++++++++++++++++++++++++

.. index::
   triple: terraform command; options; --no-show-output
.. index::
   triple: terraform command; options; --show-output

The **--show-output** flag will cause verbose output from the underlying terraform operations to be written to standard out
of the ``terraform-worker`` process.

\-\-terraform-bin
+++++++++++++++++

.. index::
   triple: terraform command; options; --terraform-bin

The **--terraform-bin** option allows a user to specify a specific terraform binary.

.. code-block:: bash

   % worker terraform --apply --terraform--bin ~/apps/terraform

.. _base-64-option:

\-\-b64-encode-hook-values / \-\-no-b64-encode-hook-values
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. index::
   triple: terraform command; options; --no-b64-encode-hook-values
.. index::
   triple: terraform command; options; --b64-encode-hook-values

The **--b64-encode-hook-values** flag will cause variable and output values that are made available to ``terraform-worker``
hooks to be base64 encoded.  This is useful since these values can be complex data structures that are not easily escaped
in an environment variable.

.. seealso::
   :doc:`./hooks`

\-\-terraform-modules-dir
+++++++++++++++++++++++++

.. index::
   triple: terraform command; options; --terraform-modules-dir

The **--terraform-modules--dir** option allows a user to specify a local directory where terraform-modules can be found.
If this value is not set, the location is assumed to be ``./terraform-modules``.

.. seealso::
   :ref:`terraform-modules`

\-\-limit
+++++++++

.. index::
   triple: terraform command; options; --limit

The **--limit** option is a repeatable option which allows a user to limit terraform operations to only specific
configuration definitions.

.. code-block:: bash

   % worker terraform --apply --limit alpha --limit omega

clean
-----

.. index::
   pair: commands; clean

The **clean** command is used to initiate operations related to removing artifacts left over
from previous runs of the ``terraform-worker``.  For example, for a ``terraform-worker`` configuration
that uses an AWS/S3 backend store, the **clean** command will remove the DynamoDB tables associated
with the backend's locking mechanism.

\-\-limit
+++++++++

.. index::
   triple: --config-file ./worker.yaml clean command; options; --limit

The **--limit** option is a repeatable option which allows a user to limit clean operations to only specific
configuration definitions.

.. code-block:: bash

   % worker --config-file ./worker.yaml clean --apply --limit alpha --limit omega
