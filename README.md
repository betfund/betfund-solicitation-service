# betfund-solicitation-service
Prefect workflow to handle solicitation.

## Installation

`pip install git+https://github.com/betfund/betfund-solicitation-service.git`

## Usage

```bash
$ export DB_CONNECTION_STRING={betfund-db-connection-string}
$ export SENDGRID_API_KEY={sendgrid-api-key}
$ export AWS_ACCESS_KEY={aws-access-key}  # not needed if `aws configure`
$ export AWS_SECRET_KEY={aws-secret-key}  # not needed if `aws configure`
```

#### Help

Get help on possible arguments.

```bash
$ betfund-solicitation-service run --help
$ betfund-solicitation-service register --help
```

#### Run

Arguments:
- `--scheduled`: Will use a scheduling manager provided by Prefect.
- `--distributed`: Will use a Dask distributed computing environment.

Runs the solicitation service flow.

```bash
$ betfund-solicitation-service run
```

#### Register

Registers the solicitation service flow to Prefect Cloud.

```bash
$ betfund-solicitation-service register
```
