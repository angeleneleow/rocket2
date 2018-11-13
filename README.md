# 🚀 Rocket 2.0

[![Build Status](https://travis-ci.org/ubclaunchpad/rocket2.0.svg?branch=master)](https://travis-ci.org/ubclaunchpad/rocket2.0)
[![codecov](https://codecov.io/gh/ubclaunchpad/rocket2.0/branch/master/graph/badge.svg)](https://codecov.io/gh/ubclaunchpad/rocket2.0)
[![Deployed with Inertia](https://img.shields.io/badge/deploying%20with-inertia-blue.svg)](https://github.com/ubclaunchpad/inertia)
[![Documentation Status](https://readthedocs.org/projects/rocket20/badge/?version=latest)](https://rocket20.readthedocs.io/en/latest/?badge=latest)

Rocket 2.0 is a from-the-ground-up rebuild of [Rocket](https://github.com/ubclaunchpad/rocket),
UBC Launch Pad's in-house management Slack bot.

## Developer Installation

We use [pipenv](https://pipenv.readthedocs.io/en/latest/) for dependency management.

```bash
git clone https://github.com/ubclaunchpad/rocket2.0.git
cd rocket2.0/
pip install pipenv
pipenv install --dev
```

`pipenv` will manage a [virtualenv](https://virtualenv.pypa.io/en/stable/),
so interacting with the program or using the development tools has to be done
through pipenv, like so:

```bash
pipenv run pycodestyle .
```

This can get inconvenient, so you can instead create a shell that runs in the managed
environment like so:

```bash
pipenv shell
```

and then commands like `pycodestyle` and `pytest` can be run like normal.

Additionally, we use [Travis CI](https://travis-ci.org/ubclaunchpad/rocket2.0) as
a CI system. To run the same checks locally, we provide `scripts/build_check.sh`;
this can be run with:

```bash
./scripts/build_check.sh
```

The above tests would be run with the assumption that other applications, such
as the local database, is also running. To run tests that explicitly do **not**
involve the running of any database, run pytest with the following arguments:

```bash
pytest -m "not db"
```

You can also install it as a
[pre-commit hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) for git:

```bash
cd scripts/
make install
```

### Testing the Database Locally

Some tests must also be run on the DynamoDB database. We recommend that you
download it and keep it running in the background while executing tests.

```bash
wget https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz
mkdir DynamoDB
tar -xvf dynamodb_local_latest.tar.gz --directory DynamoDB

# Configure AWS
scripts/setup_localaws.sh

# Run DynamoDB through Java
cd DynamoDB/
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
```
