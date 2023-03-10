# MLFlow Backend Plugin For Anaconda Enterprise Projects

## Overview

Provides a plugin to leveraging project jobs within Anaconda Enterprise for MLFlow backend processing.

## Installation Guide

1. The below variables control authorization to Anaconda Enterprise. 
These should be defined as AE5 secrets for the current user.  Alternatively they can also be set within the `anaconda-project.yml` project files.
See `Variables` below for specific details on each.

    | Variable      |
    |---------------|
    | AE5_HOSTNAME  |
    | AE5_USERNAME  |
    | AE5_PASSWORD  |


2. Install the plugin:
> conda install anaconda.enterprise.mlflow.plugin.backend.project -c https://conda.anaconda.org/joshburt

3. Add the Anaconda Project Worker Command:


    Worker: 
        env_spec: default
        unix: python -m anaconda.enterprise.mlflow.plugin.backend.project.services.worker

## Variables

### Order of resolution

1. Anaconda Project Variables
2. Anaconda Enterprise Secrets

If the below variables are defined within an Anaconda Project and as secrets within Anaconda Enterprise, then the Secrets will have a higher precedence and be used. 


1. `AE5_HOSTNAME`

    **Description**
    
    * The FQDN (Fully Qualified Domain Name) for the Anaconda Enterprise deployment.


2. `AE5_USERNAME`

    **Description**
    
    * The username of the account to create the jobs with.  This should be an account who owns the project or is a collaborator on the project.


3. `AE5_PASSWORD`

    **Description**

    * The password for the user account used for start jobs.

## Usage

1. Update usages of `mlflow.projects.run` for alternate backends.

* MLFlow documentation for this command is located within [mlflow.projects.run Documentation](https://mlflow.org/docs/2.0.1/python_api/mlflow.projects.html#mlflow.projects.run). 

Specifically we need to set the `backend` to `ae-project`:

**Example**

    import mlflow
    import uuid
    
    with mlflow.start_run(run_name=f"training-{str(uuid.uuid4())}", nested=True) as run:  
            project_run = mlflow.projects.run(
                uri=".",
                entry_point="workflow_step_entry_point_for_project",
                run_id=run.info.run_id,
                env_manager="local",
                backend="ae-project",
                parameters={
                    "training_data": training_data
                },
                experiment_id=run.info.experiment_id,
                synchronous=False
            )

## Configuration Options

### Resource Profile Specification
* This plugin supports the MLFlow standard for `backend_config` to define a resource profile.

**Example Anaconda Enterprise Backend Configuration**

    {
        "resource_profile": "large"
    }

This can be provided to `mlflow.projects.run` as a dictionary, or as a file path to a json encoded file.


## Development Requirements

* conda
* anaconda-project

## Development Environment Setup

> anaconda-project prepare

## Anaconda Project Development Commands

These commands are used during develop for solution management.

| Command          | Environment  | Description                                               |
|------------------|--------------|:----------------------------------------------------------|
| clean            | Development  | Cleanup temporary project files                           |
| lint             | Development  | Perform code linting check                                |
| lint:fix         | Development  | Perform automated code formatting                         |

## References

* https://github.com/mlflow/mlflow/tree/master/tests/resources/mlflow-test-plugin
* https://github.com/criteo/mlflow-yarn/blob/master/mlflow_yarn/yarn_backend.py
* https://mlflow.org/docs/2.0.1/plugins.html#writing-your-own-mlflow-plugins


## Contributing

1. Fork the repository on GitHub
2. Create a named feature branch (like `add_component_x`)
3. Write your change
4. Write tests for your change (if applicable)
5. Run the tests, ensuring they all pass
6. Submit a Pull Request using GitHub

## License and Authors

Copyright (c) 2023 Anaconda, Inc.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.