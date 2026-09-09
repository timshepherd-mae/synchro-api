import requests

CLIENT_ID = "service-twTLdudrg0MFNtgTAuZBQkHAm"
CLIENT_SECRET = "ouuN+kxe8sYtvBxoqOh3WXLxswAmB/c+IW2ohl2RJovTa6fLlCNp1eB1zfEik94IabY0wyjoLuE3NZvXOx/OPA=="

TOKEN_URL = "https://ims.bentley.com/connect/token"
TOKEN_SCOPE = "itwin-platform"

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
