# terraform-worker

The terraform worker was a weekend project to run terraform against a series of definitions (modules). The idea was the configuration vars, provider configuration, remote state, and variables from remote state would all be dynamically generated. The purpose was for building kubernetes deployments, and allowing all of the configuration information to be stored as either yamnl files in github, or have the worker configuration generated by an API which stored all of the deployment configurations in a database.

# Using the application

The application expected a mono-repo of terraform, that was broken up into two sections, definitions (which were really just top level modules) and sub-modules. The definitions are put into a worker config in order, with the terraform variables, and remote state variables.

This application has some specifics to the implementation that was being planned, so stores certain credentials in vault, and is perspective about where remote state is stored (DynamoDB in AWS). For the project that was being worked on, this weekend hack project was used as the basis for fully featured Go application that has similar (though much expanded) functionality.

A couple of items also rely on vault, such as SSH keys, and token signing roles and certificates. These are rather implementation specific.

# Notes:
This code is uploaded just as a proof of concept to share different ways of working with terraform, and managing a set of terraform resources through the lifecycle. It's similar in nature to tools like terragrunt (though that's much more polished, though didn't fit our particular use case!) which aim to allow a set of terraform code to be made more modular and reusable across different environments.

This was built/designed around Terraform 0.11; 0.12 has some minor changes in configurations that would require updates.

Tiny change
