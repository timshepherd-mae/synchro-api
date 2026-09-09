import requests
import json


# ==========================================================
# HARD-CODED CREDENTIALS
# ==========================================================

CLIENT_ID = "service-5yLUZGZxJyiFGQYyVpduMGj9d"
CLIENT_SECRET = "zFAGd77uLQtiiI3W/4sR16cnyMK7ow0KYi1WDmDB1a1E/xaUu/+IGMMnnrGcJxW1gnTbvisGoS2I306+ijxNVg=="


# ==========================================================
# CONSTANTS
# ==========================================================

TOKEN_URL = "https://ims.bentley.com/connect/token"


# ==========================================================
# MAIN
# ==========================================================

print("Requesting access token...")
print()

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

print("HTTP Status:", response.status_code)
print()

try:
    data = response.json()

    print("Response JSON:")
    print(data)

except Exception:

    print("Raw Response:")
    print(response.text)


if response.status_code == 200:

    access_token = data.get("access_token")

    print()
    print("SUCCESS")
    print()

    print("Access token obtained.")
    print()

    print("Token length:", len(access_token))

else:

    print()
    print("FAILED")

# ==========================================================
# get user id from token
# ==========================================================

response = requests.get(
    "https://api.bentley.com/users/me",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.bentley.itwin-platform.v1+json"
    }
)

pretty_response = json.dumps(response.json(), indent=4)
print(pretty_response)