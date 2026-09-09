from __future__ import annotations

import time
import requests
import json


from typing import Any, Iterator 
from urllib.parse import urljoin 


class BentleyApiError(RuntimeError):
    """Custom exception for Bentley API errors."""
    pass


# ==========================================================
# CONFIGURATION
# ==========================================================

CLIENT_ID = "service-twTLdudrg0MFNtgTAuZBQkHAm"
CLIENT_SECRET = "ouuN+kxe8sYtvBxoqOh3WXLxswAmB/c+IW2ohl2RJovTa6fLlCNp1eB1zfEik94IabY0wyjoLuE3NZvXOx/OPA=="

TOKEN_URL = "https://ims.bentley.com/connect/token"

API_BASE_URL = "https://api.bentley.com"

TOKEN_SCOPE = "itwin-platform"

BENTLEY_ACCEPT = (
    "application/vnd.bentley.itwin-platform.v1+json"
)

BENTLEY_HEADERS = {
    "Accept": "application/vnd.bentley.itwin-platform.v1+json"
}


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


# ==========================================================
# GET USER FIELDS
# ==========================================================

def get_all_userfields(access_token: str,schedule_id: str) -> list[dict]:

    results = []

    initial_url = (
        f"https://api.bentley.com/schedules/"
        f"{schedule_id}/user-fields?$top=1000"
    )

    for page in iter_bentley_pages(
        initial_url=initial_url,
        access_token=access_token,
    ):
        results.extend(
            page.get("userFields", [])
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


# ==========================================================
# RESOLVE ENTITY 3D USER FIELDS BY NAME
# ==========================================================

def resolve_entity_userfields(
    user_fields: list[dict],
    requested_names: list[str],
) -> list[dict]:
    """
    Resolve requested Entity 3D User Field names to their API records.

    Matching is:
        - case-insensitive
        - insensitive to leading/trailing whitespace
        - restricted to category == "Entity3d"

    The returned records follow the order of requested_names.

    Raises
    ------
    ValueError
        If a requested name is blank, missing, or ambiguous.
    """
    if not requested_names:
        raise ValueError(
            "At least one User Field name must be supplied."
        )

    lookup: dict[str, list[dict]] = {}

    for user_field in user_fields:
        category = str(
            user_field.get("category", "")
        ).strip()

        if category.casefold() != "entity3d":
            continue

        name = str(
            user_field.get("name", "")
        ).strip()

        user_field_id = user_field.get("id")

        if not name or not user_field_id:
            continue

        lookup.setdefault(
            name.casefold(),
            []
        ).append(user_field)

    resolved = []
    missing = []
    ambiguous = []

    for requested_name in requested_names:
        clean_name = str(requested_name).strip()

        if not clean_name:
            missing.append("<blank name>")
            continue

        matches = lookup.get(
            clean_name.casefold(),
            []
        )

        if not matches:
            missing.append(clean_name)
            continue

        if len(matches) > 1:
            ambiguous.append(clean_name)
            continue

        resolved.append(matches[0])

    error_parts = []

    if missing:
        error_parts.append(
            "User Fields not found: "
            + ", ".join(missing)
        )

    if ambiguous:
        error_parts.append(
            "Multiple Entity3d User Fields have these names: "
            + ", ".join(ambiguous)
        )

    if error_parts:
        raise ValueError(
            "\n".join(error_parts)
        )

    return resolved


# ==========================================================
# BUILD ENTITY 3D USER FIELD TABLE
# ==========================================================

def build_entity_userfield_table(
    entities: list[dict],
    user_field_values: list[dict],
    selected_user_fields: list[dict],
) -> list[dict]:
    """
    Pivot Entity 3D User Field Value records into one row per entity.

    Output shape:

        entity_id
        <requested User Field name 1>
        <requested User Field name 2>
        ...

    Entities without a value for a selected User Field receive
    an empty string.
    """
    selected_ids = {
        user_field["id"]
        for user_field in selected_user_fields
    }

    column_name_by_id = {
        user_field["id"]: user_field["name"]
        for user_field in selected_user_fields
    }

    values_by_entity: dict[str, dict[str, object]] = {}

    for value_record in user_field_values:
        entity_id = value_record.get("entity3dId")
        user_field_id = value_record.get("userFieldId")

        if not entity_id:
            continue

        if user_field_id not in selected_ids:
            continue

        values_by_entity.setdefault(
            entity_id,
            {}
        )[user_field_id] = value_record.get("value", "")

    table = []

    for entity in entities:
        entity_id = entity.get("id")

        if not entity_id:
            continue

        entity_values = values_by_entity.get(
            entity_id,
            {}
        )

        row = {
            "entity_id": entity_id,
        }

        for user_field in selected_user_fields:
            user_field_id = user_field["id"]
            column_name = column_name_by_id[user_field_id]

            value = entity_values.get(
                user_field_id,
                ""
            )

            if value is None:
                value = ""

            row[column_name] = value

        table.append(row)

    return table


# ==========================================================
# GET CODES
# ==========================================================

def get_all_codes(access_token: str, schedule_id: str) -> list[dict]:

    results = []

    initial_url = (
        f"https://api.bentley.com/schedules/"
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


# ==========================================================
# GET ENTITIES
# ==========================================================

def get_all_entities(access_token: str, schedule_id: str) -> list[dict]:

    results = []

    initial_url = (
        f"https://api.bentley.com/schedules/"
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
# GET TASKS
# ==========================================================

def get_all_tasks(access_token: str, schedule_id: str) -> list[dict]:

    results = []

    initial_url = (
        f"https://api.bentley.com/schedules/"
        f"{schedule_id}/tasks?$top=1000"
    )

    for page in iter_bentley_pages(
        initial_url=initial_url,
        access_token=access_token,
    ):
        results.extend(
            page.get("tasks", [])
        )

    return results



# ==========================================================
#  MULTI-PAGE API REQUEST
# ==========================================================

def iter_bentley_pages(
    initial_url: str,
    access_token: str,
    *,
    accept: str = "application/vnd.bentley.itwin-platform.v1+json",
    timeout_seconds: int = 60,
    max_retries: int = 5,
) -> Iterator[dict[str, Any]]:

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {access_token}",
        "Accept": accept,
    })

    next_url: str | None = initial_url
    seen_urls: set[str] = set()

    while next_url:
        if next_url in seen_urls:
            raise BentleyApiError(
                "The API returned a next-page URL that has already been used."
            )

        seen_urls.add(next_url)

        for attempt in range(max_retries):
            response = session.get(next_url, timeout=timeout_seconds)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                delay = int(retry_after) if retry_after else 2 ** attempt
                time.sleep(delay)
                continue

            if 500 <= response.status_code < 600:
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            break
        else:
            raise BentleyApiError(
                f"Request failed after {max_retries} attempts: {next_url}"
            )

        payload = response.json()
        yield payload

        href = (
            payload.get("_links", {})
                   .get("next", {})
                   .get("href")
        )

        next_url = urljoin(next_url, href) if href else None
