#  Installation Guide

## Process

### 1. Configure Environment

The below variables control authorization to Anaconda Enterprise.
These should be defined as AE5 secrets for the current user.  Alternatively they can also be set within the `anaconda-project.yml` project files.
See `Variables` below for specific details on each.

| Variable      |
|---------------|
| AE5_HOSTNAME  |
| AE5_USERNAME  |
| AE5_PASSWORD  |


### 2. Install Plugin

> conda install anaconda.enterprise.mlflow.plugin.backend.project -c https://conda.anaconda.org/joshburt

### 3. Add the Anaconda Project Worker Command:


    Worker: 
        env_spec: default
        unix: python -m anaconda.enterprise.mlflow.plugin.backend.project.services.worker

## Variables

**Order of resolution**

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
