from __future__ import annotations

import requests
import json

# ==========================================================
# CONFIGURATION
# ==========================================================

CLIENT_ID = "service-5yLUZGZxJyiFGQYyVpduMGj9d"
CLIENT_SECRET = "zFAGd77uLQtiiI3W/4sR16cnyMK7ow0KYi1WDmDB1a1E/xaUu/+IGMMnnrGcJxW1gnTbvisGoS2I306+ijxNVg=="
SCHEDULE_ID = "840c8ec4-c626-4b65-9610-3438e2e930ec"

TOKEN_URL = "https://ims.bentley.com/connect/token"

API_BASE_URL = "https://api.bentley.com"

TOKEN_SCOPE = "itwin-platform"

BENTLEY_ACCEPT = (
    "application/vnd.bentley.itwin-platform.v1+json"
)

# ==========================================================
# AUTHENTICATION
# ==========================================================


def get_access_token() -> str:

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": TOKEN_SCOPE,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["access_token"]


def build_session(token: str) -> requests.Session:

    session = requests.Session()

    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": BENTLEY_ACCEPT,
        }
    )

    return session


# ==========================================================
# RESOURCE EXTRACTION
# ==========================================================


def get_resources(
    session: requests.Session,
    schedule_id: str,
    top: int = 20,
):

    url = (
        f"{API_BASE_URL}/schedules/"
        f"{schedule_id}/resources"
        f"?$top={top}"
    )

    print("Request URL:")
    print(url)
    print()

    response = session.get(
        url,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# MAIN
# ==========================================================


def main():

    print("Requesting access token...")

    token = get_access_token()

    print("Access token acquired.")
    print()

    with build_session(token) as session:

        data = get_resources(
            session=session,
            schedule_id=SCHEDULE_ID,
            top=50,
        )

        resources = data.get("resources", [])

        print(
            f"Resources returned: {len(resources)}"
        )

        print()

        '''
        for index, resource in enumerate(
            resources,
            start=1,
        ):

            print(
                f"{index:>2}: "
                f"{resource.get('id')} | "
                f"{resource.get('name')}"
            )
        '''
            
        print(json.dumps(resources[29], indent=4))


if __name__ == "__main__":

    try:
        main()

    except requests.HTTPError as ex:

        print()
        print("HTTP ERROR")

        if ex.response is not None:
            print(
                f"Status: "
                f"{ex.response.status_code}"
            )

            try:
                print(ex.response.json())
            except Exception:
                print(ex.response.text)

    except Exception as ex:

        print()
        print("ERROR")
        print(ex)