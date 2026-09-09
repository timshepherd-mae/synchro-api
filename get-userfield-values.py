from core.api_auth import (
    get_access_token,
)

from core.api_itwins import (
    get_projects,
)

from core.services_entities import (
    get_project_entity_userfield_table,
)

from core.outtools import (
    FILETYPE_CSV,
    compile_filename,
    print_records,
    save_response_records,
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

def main():
    print()
    print("*** Getting access token...")

    access_token = get_access_token()

    print("*** Access token obtained successfully.")

    # ------------------------------------------------------
    # GET PROJECTS
    # ------------------------------------------------------

    print()
    print("*** Getting project list...")

    projects_response = get_projects(
        access_token
    )

    projects = projects_response.get(
        "iTwins",
        [],
    )

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

    # ------------------------------------------------------
    # SELECT PROJECT
    # ------------------------------------------------------

    try:
        project = projects[PROJECT_INDEX]
    except IndexError as ex:
        raise IndexError(
            f"PROJECT_INDEX {PROJECT_INDEX} is outside "
            f"the returned project list. "
            f"Projects returned: {len(projects)}."
        ) from ex

    project_id = project.get("id")

    if not project_id:
        raise KeyError(
            "The selected project does not contain "
            "an 'id' value."
        )

    project_name = (
        project.get("displayName")
        or project.get("name")
        or project_id
    )

    print()
    print(
        f"*** Selected project: {project_name}"
    )
    print(
        f"*** Selected project ID: {project_id}"
    )

    # ------------------------------------------------------
    # RUN PROJECT SERVICE
    # ------------------------------------------------------

    print()
    print(
        "*** Building project Entity 3D "
        "User Field table..."
    )

    result = get_project_entity_userfield_table(
        access_token=access_token,
        project_id=project_id,
        requested_userfield_names=(
            REQUESTED_USER_FIELD_NAMES
        ),
        schedule_index=SCHEDULE_INDEX,
    )

    output_records = result["records"]
    schedule = result["schedule"]
    selected_userfields = (
        result["selected_userfields"]
    )

    schedule_id = schedule.get("id")
    schedule_name = (
        schedule.get("name")
        or schedule_id
    )

    print(
        "*** Project Entity 3D User Field table "
        "built successfully."
    )
    print(
        f"*** Schedule: {schedule_name}"
    )
    print(
        f"*** Schedule ID: {schedule_id}"
    )
    print(
        f"*** Output rows: {len(output_records)}"
    )

    # ------------------------------------------------------
    # PRINT RESOLVED USER FIELDS
    # ------------------------------------------------------

    print()
    print("*** Resolved User Fields:")

    print_records(
        selected_userfields,
        n=len(selected_userfields),
    )

    # ------------------------------------------------------
    # PREVIEW OUTPUT
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # SAVE OUTPUT
    # ------------------------------------------------------

    output_file = compile_filename(
        uptree=1,
        destination="data_export/test_export",
        filename=OUTPUT_FILENAME,
    )

    print()
    print(
        f"*** Saving output to "
        f"'{output_file}'..."
    )

    written_file = save_response_records(
        records=output_records,
        filename=output_file,
        filetype=OUTPUT_FILETYPE,
    )

    print(
        f"*** Output saved successfully:"
    )
    print(written_file)

    print()
    print("*** Process completed successfully.")


if __name__ == "__main__":
    main()