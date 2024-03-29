
# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

## Boostrap
```
cdk boostrap --qualifier intgrnapi
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!


## Deploy specific stage:

Supoorted options:
- dev
- qa
- stage
- rc
- prod

Should set the variable `STAGE` with one of the last values before deploy the stack. By default, the stage will be `dev`.

To deploy with a specific stage, follow these steps:

1. Set the `STAGE` variable to the desired stage value before deploying the stack. Choose one of the supported options (`dev`, `stage`, or `prod`). For example:

**Unix/Linux/macOS:**
```bash
export STAGE=stage
```

**Windows (PowerShell):**
```powershell
$env:STAGE = "stage"
```

2. Run the command `cdk deploy --all` without specifying the `--stage` parameter. 
The script will use the value of the `STAGE` variable to determine the deployment stage.

By default, if you don't set the `STAGE` variable, the deployment will be performed with the `dev` stage.

This approach allows you to deploy the stack with a specific stage by setting the `STAGE` variable accordingly before running the deployment command.


## Set Role ARN 

1. Set the `ROLE_ARN` variable to select a new assumed role PD: (The Role should exist in AWS account).


## Set env variables for current session:

**Unix/Linux/macOS:**
```bash
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_SESSION_TOKEN=
```
**Windows (PowerShell):**
```powershell
$env:AWS_ACCESS_KEY_ID = 
$env:AWS_SECRET_ACCESS_KEY = 
$env:AWS_SESSION_TOKEN = 
```


## Set Role ARN 

1. Set the `ROLE_ARN` variable to select a new assumed role PD: (The Role should exist in AWS account).


## Set packages creation:
The `PACKAGES` environment variable is set to `False` by default.

To generate a new `pip_packages_layer.zip` file with the latest information from `requirements-all-lambdas.txt`, 
you can set the value of `PACKAGES` to `True`. 
This file contains a set of packages required by all lambda functions.

**Unix/Linux/macOS:**

```bash
export PACKAGES=True
```
**Windows (PowerShell):**
```powershell
$env:PACKAGES=True
```

By following these instructions, you can control the generation of the `pip_packages_layer.zip` file based on the value of the `PACKAGES` environment variable.