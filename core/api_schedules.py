import requests

from core.api_common import (
    API_BASE_URL,
    BENTLEY_ACCEPT,
)
# ==========================================================
# GET SCHEDULES
# ==========================================================

def get_schedules(access_token: str, project_id: str) -> dict:

    headers,params = {}, {}

    headers["Authorization"] = f"Bearer {access_token}"
    headers["Accept"] = BENTLEY_ACCEPT

    params["iTwinId"] = project_id

    response = requests.get(
        f"{API_BASE_URL}/schedules",
        params=params,
        headers=headers,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()

