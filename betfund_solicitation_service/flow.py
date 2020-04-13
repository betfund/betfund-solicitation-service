from datetime import timedelta

from dask.distributed import Client
from prefect import Flow, Parameter
from prefect.engine.executors import DaskExecutor
from prefect.schedules import Schedule
from prefect.schedules.clocks import IntervalClock

from betfund_solicitation_service.tasks import (
    CleanUp,
    EvaluateStrategies,
    GetFundUserEmails,
    GetStrategies,
    SendSolicitation,
)


class SolicitationService:
    def __init__(self, distributed=False, scheduled=False):
        """Initialize the `SolicitationService` object."""

        # flow meta
        self.distributed = distributed
        self.scheduled = scheduled

    @property
    def flow(self):
        """Property that holds the flow object."""
        return self.build()

    def build(self):
        """Builds the solicitation flow."""
        strategies_task = GetStrategies()
        evaluated_task = EvaluateStrategies()
        fund_users_task = GetFundUserEmails()
        cleanup_task = CleanUp()
        send_task = SendSolicitation()

        with Flow("betfund-solicitation-flow") as flow:
            strategies = strategies_task()
            evaluated = evaluated_task.map(strategies)
            fund_users = fund_users_task.map(evaluated)
            cleanup = cleanup_task(fund_users)
            send = send_task.map(cleanup)

        if self.scheduled:
            flow.schedule = Schedule(
                clocks=[IntervalClock(interval=timedelta(minutes=1))]
            )

        return flow

    def register(self):
        """Registers the flow to Prefect Cloud."""
        self.flow.register()

    def run(self):
        """Runs the flow."""
        if self.distributed:
            client = Client(n_workers=4, threads_per_worker=1)
            executor = DaskExecutor(address=client.scheduler.address)
            self.flow.run(executor=executor)
        self.flow.run()
