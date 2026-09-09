from core.api_common import (
    API_BASE_URL,
    iter_bentley_pages,
)

# ==========================================================
# GET ENTITIES
# ==========================================================

def get_all_entities(access_token: str, schedule_id: str) -> list[dict]:

    results = []

    initial_url = (
        f"{API_BASE_URL}/schedules/"
        f"{schedule_id}/entities-3d?$top=1000"
    )

    for page in iter_bentley_pages(
        initial_url=initial_url,
        access_token=access_token,
    ):
        results.extend(
            page.get("entities3d", [])
        )

    return results

# ==========================================================
# GET ENTITY 3D USER FIELD VALUES
# ==========================================================

def get_all_entity_userfield_values(
    access_token: str,
    schedule_id: str,
) -> list[dict]:
    """
    Retrieve all Entity 3D User Field Value records for a schedule.

    Each returned record is expected to contain:

        entity3dId
        userFieldId
        value
    """
    results = []

    initial_url = (
        f"{API_BASE_URL}/schedules/"
        f"{schedule_id}/entities-3d/user-field-values"
        f"?$top=1000"
    )

    for page in iter_bentley_pages(
        initial_url=initial_url,
        access_token=access_token,
    ):
        results.extend(
            page.get("userFieldValues", [])
        )

    return results

