from core.apitools import *
from core.outtools import *


# ==========================================================
# CONFIGURATION
# ==========================================================

REQUESTED_USER_FIELD_NAMES = [
    "MAE-4D.RID",
    "Item.GUID",
    "Synchro.SynchroID",
]

OUTPUT_FILENAME = "entity_userfield_values"
OUTPUT_FILETYPE = FILETYPE_CSV

PROJECT_INDEX = 0
SCHEDULE_INDEX = 0

CONSOLE_PREVIEW_ROWS = 15

def resolve_requested_userfields(
    user_fields,
    requested_names,
):
    """
    Resolve requested User Field names to their corresponding IDs.

    Matching is:

        - case-insensitive
        - insensitive to leading/trailing spaces

    The returned records use a consistent structure:

        {
            "id": "...",
            "name": "..."
        }
    """

    indexed_user_fields = {}

    for user_field in user_fields:
        user_field_id = get_userfield_id(user_field)
        user_field_name = get_userfield_name(user_field)

        if user_field_id is None:
            continue

        if user_field_name is None:
            continue

        normalised_user_field_name = normalise_name(
            user_field_name
        )

        indexed_user_fields.setdefault(
            normalised_user_field_name,
            [],
        ).append(
            {
                "id": user_field_id,
                "name": user_field_name,
                "source": user_field,
            }
        )

    resolved_user_fields = []
    missing_names = []
    duplicate_names = []

    for requested_name in requested_names:
        normalised_requested_name = normalise_name(
            requested_name
        )

        matches = indexed_user_fields.get(
            normalised_requested_name,
            [],
        )

        if not matches:
            missing_names.append(requested_name)
            continue

        if len(matches) > 1:
            duplicate_names.append(
                {
                    "requested_name": requested_name,
                    "matches": matches,
                }
            )
            continue

        match = matches[0]

        resolved_user_fields.append(
            {
                "id": match["id"],
                "name": requested_name,
            }
        )

    if missing_names:
        formatted_missing_names = "\n".join(
            f"  - {name}"
            for name in missing_names
        )

        raise ValueError(
            "The following requested User Field names "
            "were not found:\n"
            f"{formatted_missing_names}"
        )

    if duplicate_names:
        duplicate_lines = []

        for duplicate in duplicate_names:
            matched_ids = ", ".join(
                str(match["id"])
                for match in duplicate["matches"]
            )

            duplicate_lines.append(
                f"  - {duplicate['requested_name']}: "
                f"{matched_ids}"
            )

        raise ValueError(
            "The following requested User Field names "
            "matched more than one User Field ID:\n"
            + "\n".join(duplicate_lines)
        )

    return resolved_user_fields



def build_entity_userfield_table(
    entities,
    userfield_value_records,
    selected_user_fields,
):
    """
    Build a tabulated record set with one row per Entity 3D.

    Output columns:

        entity_id
        requested User Field 1
        requested User Field 2
        ...
    """

    selected_field_ids = {
        str(user_field["id"]): user_field["name"]
        for user_field in selected_user_fields
    }

    flattened_value_records = (
        flatten_userfield_value_records(
            userfield_value_records
        )
    )

    values_by_entity = {}

    for value_record in flattened_value_records:
        entity_id = get_value_record_entity_id(
            value_record
        )

        user_field_id = get_value_record_userfield_id(
            value_record
        )

        if entity_id is None:
            continue

        if user_field_id is None:
            continue

        user_field_id_key = str(user_field_id)

        if user_field_id_key not in selected_field_ids:
            continue

        entity_id_key = str(entity_id)

        user_field_name = selected_field_ids[
            user_field_id_key
        ]

        user_field_value = get_value_record_value(
            value_record
        )

        values_by_entity.setdefault(
            entity_id_key,
            {},
        )[user_field_name] = user_field_value

    output_records = []

    for entity in entities:
        entity_id = get_entity_id(entity)

        if entity_id is None:
            continue

        entity_id_key = str(entity_id)

        output_record = {
            "entity_id": entity_id,
        }

        entity_values = values_by_entity.get(
            entity_id_key,
            {},
        )

        for selected_user_field in selected_user_fields:
            user_field_name = selected_user_field["name"]

            output_record[user_field_name] = (
                entity_values.get(
                    user_field_name,
                    "",
                )
            )

        output_records.append(output_record)

    return output_records


# ==========================================================
# MAIN
# ==========================================================

print()
print("*** Getting access token...")

access_token = get_access_token()

print("*** Access token obtained successfully.")


# ----------------------------------------------------------
# GET PROJECTS / ITWINS
# ----------------------------------------------------------

print("*** Getting project list...")

projects_response = get_projects(access_token)

projects = projects_response.get("iTwins", [])

if not projects:
    raise RuntimeError(
        "No iTwins were returned."
    )

print(
    f"*** Project list obtained successfully: "
    f"{len(projects)}"
)

print_records(
    projects,
    n=CONSOLE_PREVIEW_ROWS,
)

try:
    project = projects[PROJECT_INDEX]
except IndexError as ex:
    raise IndexError(
        f"PROJECT_INDEX {PROJECT_INDEX} is outside "
        f"the returned project list."
    ) from ex

project_id = project.get("id")

if not project_id:
    raise KeyError(
        "The selected project record does not contain "
        "an 'id' value."
    )

print()
print(
    f"*** Selected project: "
    f"{project.get('name', project_id)}"
)
print(
    f"*** Selected project ID: "
    f"{project_id}"
)


# ----------------------------------------------------------
# GET SCHEDULES
# ----------------------------------------------------------

print()
print(
    f"*** Getting schedules from "
    f"Project={PROJECT_INDEX}..."
)

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
        "No schedules were returned for the selected iTwin."
    )

print(
    f"*** Schedules obtained successfully: "
    f"{len(schedules)}"
)

print_records(
    schedules,
    n=CONSOLE_PREVIEW_ROWS,
)

try:
    schedule = schedules[SCHEDULE_INDEX]
except IndexError as ex:
    raise IndexError(
        f"SCHEDULE_INDEX {SCHEDULE_INDEX} is outside "
        f"the returned schedule list."
    ) from ex

schedule_id = schedule.get("id")

if not schedule_id:
    raise KeyError(
        "The selected schedule record does not contain "
        "an 'id' value."
    )

print()
print(
    f"*** Selected schedule: "
    f"{schedule.get('name', schedule_id)}"
)
print(
    f"*** Selected schedule ID: "
    f"{schedule_id}"
)


# ----------------------------------------------------------
# GET USER FIELD DEFINITIONS
# ----------------------------------------------------------

print()
print(
    f"*** Getting User Fields from "
    f"Schedule={SCHEDULE_INDEX}..."
)

user_fields = get_all_userfields(
    access_token,
    schedule_id,
)

if not user_fields:
    raise RuntimeError(
        "No User Fields were returned for the "
        "selected schedule."
    )

print(
    f"*** User Fields obtained successfully: "
    f"{len(user_fields)}"
)


# ----------------------------------------------------------
# RESOLVE REQUESTED USER FIELD NAMES
# ----------------------------------------------------------

print()
print(
    "*** Resolving requested Entity 3D User Fields..."
)

selected_user_fields = resolve_requested_userfields(
    user_fields=user_fields,
    requested_names=REQUESTED_USER_FIELD_NAMES,
)

print(
    "*** Requested User Fields resolved successfully."
)

print_records(
    selected_user_fields,
    n=len(selected_user_fields),
)


# ----------------------------------------------------------
# GET ENTITY 3D RECORDS
# ----------------------------------------------------------

print()
print(
    f"*** Getting Entity 3D records from "
    f"Schedule={SCHEDULE_INDEX}..."
)

entities = get_all_entities(
    access_token,
    schedule_id,
)

if not entities:
    raise RuntimeError(
        "No Entity 3D records were returned for the "
        "selected schedule."
    )

print(
    f"*** Entity 3D records obtained successfully: "
    f"{len(entities)}"
)


# ----------------------------------------------------------
# GET ENTITY 3D USER FIELD VALUES
# ----------------------------------------------------------

print()
print(
    "*** Getting Entity 3D User Field values..."
)

entity_user_field_values = (
    get_all_entity_userfield_values(
        access_token,
        schedule_id,
    )
)

print(
    f"*** Entity 3D User Field values obtained "
    f"successfully: "
    f"{len(entity_user_field_values)}"
)


# ----------------------------------------------------------
# BUILD TABULATED OUTPUT
# ----------------------------------------------------------

print()
print(
    "*** Building tabulated Entity 3D User Field output..."
)

output_records = build_entity_userfield_table(
    entities=entities,
    userfield_value_records=entity_user_field_values,
    selected_user_fields=selected_user_fields,
)

if not output_records:
    raise RuntimeError(
        "No output records were created."
    )

print(
    f"*** Tabulated output created successfully: "
    f"{len(output_records)} rows"
)


# ----------------------------------------------------------
# CONSOLE PREVIEW
# ----------------------------------------------------------

print()
print(
    f"*** Previewing first "
    f"{min(CONSOLE_PREVIEW_ROWS, len(output_records))} "
    f"output rows..."
)

print_records(
    output_records,
    n=CONSOLE_PREVIEW_ROWS,
)


# ----------------------------------------------------------
# SAVE OUTPUT
# ----------------------------------------------------------

OUTPUT_FILENAME = compile_filename(
    uptree=1,
    destination="data_export/test_export",
    filename="entity_userfield_values"
)


print()
print(
    f"*** Saving output to "
    f"'{OUTPUT_FILENAME}'..."
)

save_response_records(
    records=output_records,
    filename=OUTPUT_FILENAME,
    filetype=OUTPUT_FILETYPE,
)

print("*** Output saved successfully.")

print()
print("*** Process completed successfully.")