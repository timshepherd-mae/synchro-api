from __future__ import annotations

import os
import sys
from typing import Any

import requests


TOKEN_URL = "https://ims.bentley.com/connect/token"
API_BASE_URL = "https://api.bentley.com"

BENTLEY_ACCEPT = "application/vnd.bentley.itwin-platform.v1+json"
TOKEN_SCOPE = "itwin-platform"


def required_environment_variable(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(
            f"Required environment variable {name!r} is not defined."
        )

    return value.strip()


def get_access_token(
    client_id: str,
    client_secret: str,
) -> str:
    """
    Obtain a Bentley OAuth access token using Client Credentials flow.
    """

    form_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": TOKEN_SCOPE,
        "grant_type": "client_credentials",
    }

    response = requests.post(
        TOKEN_URL,
        data=form_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=30,
    )

    response.raise_for_status()

    token_response = response.json()

    access_token = token_response.get("access_token")

    if not access_token:
        raise RuntimeError(
            "Bentley token response did not contain an access_token."
        )

    return str(access_token)


def build_api_session(access_token: str) -> requests.Session:
    """
    Create a reusable session containing the standard Bentley headers.
    """

    session = requests.Session()

    session.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
            "Accept": BENTLEY_ACCEPT,
        }
    )

    return session


def get_schedule(
    session: requests.Session,
    schedule_id: str,
) -> dict[str, Any]:
    """
    Retrieve the details of one known schedule.
    """

    url = f"{API_BASE_URL}/schedules/{schedule_id}"

    response = session.get(url, timeout=30)
    response.raise_for_status()

    return response.json()


def get_tasks(
    session: requests.Session,
    schedule_id: str,
    page_size: int = 100,
) -> list[dict[str, Any]]:
    """
    Retrieve task records, following Bentley's returned next-page link.

    The name of the returned collection is expected to be 'tasks'.
    """

    if page_size < 1 or page_size > 10000:
        raise ValueError("page_size must be between 1 and 10000.")

    url: str | None = (
        f"{API_BASE_URL}/schedules/{schedule_id}/tasks"
        f"?$top={page_size}"
    )

    tasks: list[dict[str, Any]] = []

    while url:
        response = session.get(url, timeout=60)
        response.raise_for_status()

        page = response.json()

        page_tasks = page.get("tasks", [])

        if not isinstance(page_tasks, list):
            raise RuntimeError(
                "Unexpected Bentley response: 'tasks' is not a list."
            )

        tasks.extend(page_tasks)

        links = page.get("_links", {})
        next_link = links.get("next")

        if isinstance(next_link, dict):
            url = next_link.get("href")
        else:
            url = None

    return tasks


def main() -> int:
    client_id = required_environment_variable("BENTLEY_CLIENT_ID")
    client_secret = required_environment_variable(
        "BENTLEY_CLIENT_SECRET"
    )
    schedule_id = required_environment_variable(
        "BENTLEY_SCHEDULE_ID"
    )

    print("Requesting Bentley access token...")

    access_token = get_access_token(
        client_id=client_id,
        client_secret=client_secret,
    )

    print("Access token obtained.")

    with build_api_session(access_token) as session:
        print("\nRetrieving schedule details...")

        schedule_response = get_schedule(
            session=session,
            schedule_id=schedule_id,
        )

        schedule = schedule_response.get(
            "schedule",
            schedule_response,
        )

        print(f"Schedule ID:   {schedule.get('id')}")
        print(f"Schedule name: {schedule.get('name')}")
        print(f"Schedule type: {schedule.get('type')}")

        print("\nRetrieving tasks...")

        tasks = get_tasks(
            session=session,
            schedule_id=schedule_id,
            page_size=100,
        )

        print(f"Tasks returned: {len(tasks)}")

        for task in tasks[:10]:
            print(
                f"{task.get('id')} | "
                f"{task.get('name')} | "
                f"{task.get('startDate')} | "
                f"{task.get('finishDate')}"
            )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except requests.HTTPError as exc:
        response = exc.response

        print(
            f"HTTP request failed: "
            f"{response.status_code} {response.reason}",
            file=sys.stderr,
        )

        try:
            print(response.json(), file=sys.stderr)
        except ValueError:
            print(response.text, file=sys.stderr)

        raise SystemExit(1)

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)