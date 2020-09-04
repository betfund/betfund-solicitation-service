import functools

import click

from betfund_solicitation_service.flow import SolicitationService


@click.group()
def cli():
    pass


def common_options(f):
    options = [
        click.option("-d", "--distributed", is_flag=True, help="Run distributed."),
        click.option("-s", "--scheduled", is_flag=True, help="Run on schedule."),
    ]
    return functools.reduce(lambda x, opt: opt(x), options, f)


@cli.command()
@common_options
def run(distributed, scheduled):
    service = SolicitationService(distributed=distributed, scheduled=scheduled)
    service.run()


@cli.command()
@common_options
def register(distributed, scheduled):
    service = SolicitationService(distributed=distributed, scheduled=scheduled)
    service.register()


if __name__ == "__main__":
    cli()
