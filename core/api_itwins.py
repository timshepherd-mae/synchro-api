import requests

from core.api_common import (
    API_BASE_URL,
    BENTLEY_ACCEPT,
)

# ==========================================================
# GET PROJECTS
# ==========================================================

def get_projects(access_token: str) -> dict:

    headers = {}

    headers["Authorization"] = f"Bearer {access_token}"
    headers["Accept"] = BENTLEY_ACCEPT

    response = requests.get(
        f"{API_BASE_URL}/itwins",
        headers=headers,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()