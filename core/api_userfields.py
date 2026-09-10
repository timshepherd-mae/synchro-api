from core.api_common import (
    API_BASE_URL,
    iter_bentley_pages,
)

# ==========================================================
# DEFINE USERFIELD CATEGORIES
# ==========================================================

VALID_USERFIELD_CATEGORIES = {
    "Task",
    "Entity3d",
    "Resource",
    "ResourceGroup",
}


# ==========================================================
# GET USER FIELDS
# ==========================================================

def get_all_userfields(
        access_token: str,
        schedule_id: str, 
        category: str | None = None,
) -> list[dict]:

    results = []

    initial_url = (
        f"{API_BASE_URL}/schedules/"
        f"{schedule_id}/user-fields?$top=1000"
    )

    for page in iter_bentley_pages(
        initial_url=initial_url,
        access_token=access_token,
    ):
        results.extend(
            page.get("userFields", [])
        )

    filtered_results = filter_userfields(
        userfields=results,
        category=category,
    )

    return filtered_results


# ==========================================================
# FILTER USERFIELDS
# ==========================================================

def filter_userfields(
    userfields: list[dict],
    category: str | None = None,
) -> list[dict]:

    if category is None:
        return userfields

    if category not in VALID_USERFIELD_CATEGORIES:
        raise ValueError(
            f"Unsupported category '{category}'. "
            f"Expected one of: "
            f"{', '.join(sorted(VALID_USERFIELD_CATEGORIES))}"
        )

    return [
        uf
        for uf in userfields
        if uf.get("category") == category
    ]


def resolve_userfield(
    userfields: list[dict],
    name: str,
    category: str | None = None,
) -> dict:

    matches = [
        uf
        for uf in userfields
        if uf.get("name") == name
    ]

    if category is not None:
        matches = [
            uf
            for uf in matches
            if uf.get("category") == category
        ]

    if not matches:
        raise ValueError(
            f"No User Field found for "
            f"name='{name}'"
            + (
                f", category='{category}'"
                if category
                else ""
            )
        )

    if len(matches) > 1:
        categories = sorted(
            {
                uf.get("category")
                for uf in matches
            }
        )

        raise ValueError(
            f"Ambiguous User Field "
            f"name='{name}'. "
            f"Found in categories: "
            f"{', '.join(categories)}. "
            f"Specify category."
        )

    return matches[0]


def resolve_userfield_id(
    userfields: list[dict],
    name: str,
    category: str | None = None,
) -> str:

    return resolve_userfield(
        userfields=userfields,
        name=name,
        category=category,
    )["id"]
