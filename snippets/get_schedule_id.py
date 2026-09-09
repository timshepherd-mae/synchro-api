from __future__ import annotations
import token
from urllib import response

import requests

# ==========================================================
# CONFIGURATION
# ==========================================================

CLIENT_ID = "service-5yLUZGZxJyiFGQYyVpduMGj9d"
CLIENT_SECRET = "zFAGd77uLQtiiI3W/4sR16cnyMK7ow0KYi1WDmDB1a1E/xaUu/+IGMMnnrGcJxW1gnTbvisGoS2I306+ijxNVg=="

# iTwin containing the SYNCHRO schedule
ITWIN_ID = "840c8ec4-c626-4b65-9610-3438e2e930ec"
# ITWIN_ID = "8f650409-fca6-4ff9-b1bd-a012bbfc8431"


TOKEN_URL = "https://ims.bentley.com/connect/token"
API_BASE = "https://api.bentley.com"

ACCEPT_HEADER = "application/vnd.bentley.itwin-platform.v1+json"


# ==========================================================
# AUTHENTICATION
# ==========================================================

def get_access_token() -> str:

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "scope": "itwin-platform",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=30,
    )

    response.raise_for_status()

    token_json = response.json()

    return token_json["access_token"]


# ==========================================================
# ITWIN DISCOVERY
# ==========================================================

def get_itwin(access_token: str) -> dict:

    response = requests.get(
        f"{API_BASE}/itwins",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": ACCEPT_HEADER
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# SCHEDULE DISCOVERY
# ==========================================================

def get_schedules(access_token: str) -> dict:

    response = requests.get(
        f"{API_BASE}/schedules",
        params={
            "iTwinId": ITWIN_ID
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": ACCEPT_HEADER
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("Authenticating...")

    token = get_access_token()

    print("Authentication OK")
    print()

    print(f"Searching schedules in iTwin:")
    print(ITWIN_ID)
    print()

    # ==========================================================
    result = get_itwin(token)
    print(result)
    # ==========================================================

    result = get_schedules(token)

    schedules = result.get("schedules", [])

    if not schedules:

        print("No schedules returned.")
        return

    print(f"Found {len(schedules)} schedule(s)")
    print()

    for i, schedule in enumerate(schedules, start=1):

        print("-" * 80)
        print(f"Schedule #{i}")

        print("Name:")
        print(schedule.get("name"))

        print()

        print("Schedule ID:")
        print(schedule.get("id"))

        print()

        print("Type:")
        print(schedule.get("type"))

        print()

        print("iModel ID:")
        print(schedule.get("iModelId"))

        print()

        print("iTwin ID:")
        print(schedule.get("iTwinId"))

        print()

    print("-" * 80)


if __name__ == "__main__":

    try:
        main()

    except requests.HTTPError as ex:

        print()
        print("HTTP ERROR")

        if ex.response is not None:

            print("Status:", ex.response.status_code)

            try:
                print(ex.response.json())
            except Exception:
                print(ex.response.text)

    except Exception as ex:

        print()
        print("ERROR")
        print(ex)