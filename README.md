# betfund-solicitation-service
Prefect workflow to handle solicitation.

## Installation

`pip install git+https://github.com/betfund/betfund-solicitation-service.git`

## Usage

```bash
$ export DB_CONNECTION_STRING={betfund-db-connection-string}
$ export SENDGRID_API_KEY={sendgrid-api-key}
```

#### Help

Get help on possible arguments.

```bash
$ betfund-solicitation-service run --help
$ betfund-solicitation-service register --help
```

#### Run

Runs the solicitation service flow.

```bash
$ betfund-solicitation-service run --scheduled
```

#### Register

Registers the solicitation service flow to Prefect Cloud.

```bash
$ betfund-solicitation-service register --distributed
```