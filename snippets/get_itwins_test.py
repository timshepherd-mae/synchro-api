import requests

# ==========================================================
# CONFIGURATION
# ==========================================================

CLIENT_ID = "service-5yLUZGZxJyiFGQYyVpduMGj9d"
CLIENT_SECRET = "zFAGd77uLQtiiI3W/4sR16cnyMK7ow0KYi1WDmDB1a1E/xaUu/+IGMMnnrGcJxW1gnTbvisGoS2I306+ijxNVg=="

TOKEN_URL = "https://ims.bentley.com/connect/token"

API_HEADERS = {
    "Accept": "application/vnd.bentley.itwin-platform.v1+json"
}


# ==========================================================
# GET ACCESS TOKEN
# ==========================================================

def get_access_token():

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

    return response.json()["access_token"]


# ==========================================================
# GET MY ITWINS
# ==========================================================

def get_my_itwins(token):

    headers = API_HEADERS.copy()

    headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        "https://api.bentley.com/itwins",
        headers=headers,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


# ==========================================================
# MAIN
# ==========================================================

try:

    print("Getting access token...")
    token = get_access_token()

    print("Token OK")
    print()

    print("Querying iTwins...")

    result = get_my_itwins(token)

    print()
    print("=" * 80)
    print("RAW RESPONSE")
    print("=" * 80)
    print()

    print(result)

    print()
    print("=" * 80)

    itwins = result.get("iTwins", [])

    print(f"Found {len(itwins)} iTwin(s)")
    print()

    for idx, itwin in enumerate(itwins, start=1):

        print("-" * 80)
        print(f"iTwin #{idx}")

        print(
            "Display Name:",
            itwin.get("displayName")
        )

        print(
            "iTwin ID:",
            itwin.get("id")
        )

        print(
            "Type:",
            itwin.get("type")
        )

        print(
            "Status:",
            itwin.get("status")
        )

        print()

except requests.HTTPError as ex:

    print()
    print("HTTP ERROR")

    if ex.response is not None:

        print("Status Code:", ex.response.status_code)

        try:
            print(ex.response.json())
        except Exception:
            print(ex.response.text)

except Exception as ex:

    print()
    print("ERROR")
    print(ex)
