import os
import requests

TOKEN_URL = "https://ims.bentley.com/connect/token"
TOKEN_SCOPE = "itwin-platform"

CLIENT_ID = os.getenv("BENTLEY_CLIENT_ID")
CLIENT_SECRET = os.getenv("BENTLEY_CLIENT_SECRET")

if not CLIENT_ID:
    raise RuntimeError(
        "BENTLEY_CLIENT_ID environment variable "
        "is not configured."
    )

if not CLIENT_SECRET:
    raise RuntimeError(
        "BENTLEY_CLIENT_SECRET environment variable "
        "is not configured."
    )

# ==========================================================
# ACCESS TOKEN
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
