from core.apitools import *
from core.outtools import *
from core.services_userfields import (
    get_entity_userfield_table,
)


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
# BUILD TABULATED OUTPUT
# ----------------------------------------------------------

print()
print(
    "*** Building tabulated Entity 3D User Field output..."
)

output_records = get_entity_userfield_table(
    access_token=access_token,
    project_id=project_id,
    requested_userfield_names=REQUESTED_USER_FIELD_NAMES,
    schedule_index=SCHEDULE_INDEX,
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