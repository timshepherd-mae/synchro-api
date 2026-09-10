from core.api_schedules import (
    get_schedules,
)

from core.api_entities import (
    get_all_entities,
    get_all_entity_userfield_values,
)

from core.api_userfields import (
    get_all_userfields,
)

from core.data_userfields import (
    resolve_entity_userfields,
    build_entity_userfield_table,
)


# ==========================================================
# PROJECT ENTITY USER FIELD TABLE
# ==========================================================

def get_project_entity_userfield_table(
    access_token: str,
    project_id: str,
    requested_userfield_names: list[str],
    schedule_index: int = 0,
    userfield_category: str | None = "Entity3d",
) -> dict:
    """
    Build an Entity 3D User Field table for one Bentley project.

    The project is supplied using project_id. This service discovers
    the project's schedules and selects one using schedule_index.

    Parameters
    ----------
    access_token : str
        Bentley access token.

    project_id : str
        Bentley iTwin/project ID.

    requested_userfield_names : list[str]
        Entity 3D User Field names to include in the output.

    schedule_index : int
        Zero-based schedule index. Defaults to the first schedule.

    Returns
    -------
    dict
        A result containing:

        {
            "project_id": "...",
            "schedule": {...},
            "selected_userfields": [...],
            "records": [...]
        }

    Raises
    ------
    ValueError
        If project_id or requested_userfield_names is missing.

    RuntimeError
        If no schedules, User Fields or Entity 3D records are found.

    IndexError
        If schedule_index is outside the available schedule list.
    """

    # ------------------------------------------------------
    # VALIDATE INPUTS
    # ------------------------------------------------------

    if not project_id:
        raise ValueError(
            "project_id must be supplied."
        )

    if not requested_userfield_names:
        raise ValueError(
            "At least one User Field name must be supplied."
        )

    # ------------------------------------------------------
    # GET PROJECT SCHEDULES
    # ------------------------------------------------------

    schedules_response = get_schedules(
        access_token,
        project_id,
    )

    schedules = schedules_response.get(
        "schedules",
        [],
    )

    if not schedules:
        raise RuntimeError(
            f"No schedules were returned for project "
            f"{project_id}."
        )

    # ------------------------------------------------------
    # SELECT SCHEDULE
    # ------------------------------------------------------

    try:
        schedule = schedules[schedule_index]
    except IndexError as ex:
        raise IndexError(
            f"schedule_index {schedule_index} is outside "
            f"the available schedule range for project "
            f"{project_id}. "
            f"Schedules returned: {len(schedules)}."
        ) from ex

    schedule_id = schedule.get("id")

    if not schedule_id:
        raise KeyError(
            "The selected schedule does not contain an "
            "'id' value."
        )

    # ------------------------------------------------------
    # GET USER FIELD DEFINITIONS
    # ------------------------------------------------------

    user_fields = get_all_userfields(
        access_token=access_token,
        schedule_id=schedule_id,
        category=userfield_category,
    )

    if not user_fields:
        category_context = (
            f" in category '{userfield_category}'"
            if userfield_category is not None
            else ""
        )

        raise RuntimeError(
            f"No User Fields were returned for schedule "
            f"{schedule_id}{category_context}."
        )

    # ------------------------------------------------------
    # RESOLVE REQUESTED USER FIELD NAMES
    # ------------------------------------------------------

    selected_userfields = resolve_entity_userfields(
        user_fields=user_fields,
        requested_names=requested_userfield_names,
        allow_missing=True
    )

    resolved_names = {
        field["name"]
        for field in selected_userfields
    }

    missing_names = [
        name
        for name in requested_userfield_names
        if name not in resolved_names
    ]

    if missing_names:
        print()
        print(
            "WARNING: The following User Fields "
            "were not found:"
        )

        for name in missing_names:
            print(f"    {name}")

            
    # ------------------------------------------------------
    # GET ENTITY 3D RECORDS
    # ------------------------------------------------------

    entities = get_all_entities(
        access_token,
        schedule_id,
    )

    if not entities:
        raise RuntimeError(
            f"No Entity 3D records were returned for "
            f"schedule {schedule_id}."
        )

    # ------------------------------------------------------
    # GET ENTITY 3D USER FIELD VALUES
    # ------------------------------------------------------

    entity_userfield_values = (
        get_all_entity_userfield_values(
            access_token,
            schedule_id,
        )
    )

    # ------------------------------------------------------
    # BUILD OUTPUT TABLE
    # ------------------------------------------------------

    output_records = build_entity_userfield_table(
        entities=entities,
        userfield_value_records=entity_userfield_values,
        selected_user_fields=selected_userfields,
    )

    if not output_records:
        raise RuntimeError(
            f"No output records were created for project "
            f"{project_id}, schedule {schedule_id}."
        )

    # ------------------------------------------------------
    # RETURN RECORDS AND CONTEXT
    # ------------------------------------------------------

    return output_records