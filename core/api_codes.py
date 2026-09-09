from core.api_common import (
    API_BASE_URL,
    iter_bentley_pages,
)

# ==========================================================
# GET CODES
# ==========================================================

def get_all_codes(access_token: str, schedule_id: str) -> list[dict]:

    results = []

    initial_url = (
        f"{API_BASE_URL}/schedules/"
        f"{schedule_id}/codes?$top=1000"
    )

    for page in iter_bentley_pages(
        initial_url=initial_url,
        access_token=access_token,
    ):
        results.extend(
            page.get("codes", [])
        )

    return results