import datetime
import json
import os
from collections import defaultdict
from functools import partial
from itertools import chain, groupby
from operator import is_not

from dateutil.parser import parse
from dotenv import load_dotenv
from prefect import Task
from prefect.tasks.secrets import EnvVarSecret
from sqlalchemy import create_engine

load_dotenv()


class GetStrategies(Task):
    """Subclass `GetStrategies` of `prefect.Task`"""

    def __init__(self, **kwargs):
        self.connection_string = os.environ.get("DB_CONNECTION_STRING")
        super().__init__(**kwargs)

    def run(self):
        """
        Uses SQLAlchemy engine connection to retrieve all
        fund solicitation schedules.
        """

        # Connect to SQLAlchemy
        engine = create_engine(self.connection_string)

        # Execute query
        with engine.connect() as connection:
            query = """
                SELECT
                    funds.id AS id,
                    funds.name AS name,
                    strategies.details AS strategy_details
                FROM funds
                JOIN strategies
                ON funds.strategy_id = strategies.id
            """
            params = dict()
            rows = connection.execute(query, **params)

            results = [dict(row.items()) for row in rows.fetchall()]

        return results


class EvaluateStrategies(Task):
    """Subclass `EvaluateStrategies` of `prefect.Task`"""

    def run(self, fund):
        """
        Evaluates whether to send a solicitation email notification
        to fund members, given the solicitation start date and
        timedelta defined by fund owner.
        """

        # Convert stringified strategy JSON to dictionary
        strategy = json.loads(fund["strategy_details"])

        # Handle datetimes and timedeltas
        now = datetime.datetime.utcnow().replace(microsecond=0, second=0)
        start = parse(strategy["solicitation_start"]).replace(second=0)
        schedule = strategy["solicitation_schedule"]
        delta = now - start

        # Assess if now is the time to send email
        if schedule == "hourly":
            if (delta.seconds / 60 / 60) == 1:
                return record
        if schedule == "daily":
            if (delta.seconds / 60 / 60 / 24) == 1:
                return record
        if schedule == "weekly":
            if (delta.seconds / 60 / 60 / 24 / 7) == 1:
                return record


class GetFundUserEmails(Task):
    """Subclass `GetFundUserEmails` of `prefect.Task`"""

    def __init__(self, **kwargs):
        self.connection_string = os.environ.get("DB_CONNECTION_STRING")
        super().__init__(**kwargs)

    def run(self, valid_fund):
        """
        Gets emails for funds that have passed through evaluation criteria.
        """

        if valid_fund:

            # Connect to SQLAlchemy
            engine = create_engine(self.connection_string)

            # Execute query
            with engine.connect() as connection:
                query = """
                    WITH owner_cte AS (
                        SELECT
                            funds.id AS fund_id,
                            funds.owner_id AS owner_id,
                            users.email_address AS owner_email
                        FROM
                            funds
                        JOIN
                            users
                        ON
                            funds.owner_id == users.id
                    )
                    SELECT
                        users.first_name AS first_name,
                        users.last_name AS last_name,
                        users.email_address AS email,
                        funds.id AS fund_id,
                        funds.name AS fund_name,
                        funds.description AS fund_description,
                        owner_cte.owner_email AS owner_email
                    FROM
                        fund_users
                    JOIN
                        users
                    ON
                        users.id = fund_users.user_id
                    JOIN
                        funds
                    ON
                        funds.id = fund_users.fund_id
                    JOIN
                        owner_cte
                    ON
                        owner_cte.fund_id = fund_users.fund_id
                    WHERE
                        funds.id = :fund_id
                """
                params = dict(fund_id=valid_fund["id"])
                rows = connection.execute(query, **params)

                results = [dict(row.items()) for row in rows.fetchall()]

            return results


class CleanUp(Task):
    """Subclass `CleanUp` of `prefect.Task`"""

    def run(self, final_emails):
        """
        Cleans up None returns from previous tasks, creates final
        merged list ready for email sending.
        """

        # Remove all None elements
        cleaned = filter(partial(is_not, None), final_emails)

        # Merge list of lists
        merged = list(chain(*cleaned))

        # Grouping by fund id
        key = lambda d: d["fund_id"]
        final = [list(grp) for _, grp in groupby(sorted(merged, key=key), key)]

        return final


class SendSolicitation(Task):
    """Subclass `SendSolicitation` of `prefect.Task`"""

    def __init__(self, **kwargs):
        self.sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
        super().__init__(**kwargs)

    def run(self, email_group):
        """
        Sends solicitation email to fund members from fund owner.
        """

        body_html = """
            <h1>Hello, {} {}:</h1>
            <p>You have a new solicitation request for {} (ID#: {}).</p>
        """

        for user in email_group:
            message = Message(
                f"Solicitation Email for FundID: {user['fund_id']}",
                sender=user["owner_email"],
                to=user["email"],
                subject=f"Solicitation Alert! ({user['fund_name']})",
                body_html=body_html.format(
                    user["first_name"],
                    user["last_name"],
                    user["fund_name"],
                    user["fund_id"],
                ),
            )
            sg = SendGrid(msg, self.sendgrid_api_key)
            sg.send()
