from core.api_auth import get_access_token
from core.api_itwins import get_projects

from core.dialogtools import select_projects

from core.services_entities import (
    get_project_entity_userfield_table,
)

from core.outtools import (
    FILETYPE_CSV,
    build_project_label,
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

OUTPUT_FILENAME = "sid_rid_guid_table.csv"
OUTPUT_FILETYPE = FILETYPE_CSV

SCHEDULE_INDEX = 0
CONSOLE_PREVIEW_ROWS = 15

OUTPUT_DESTINATION = (
    "data_export/test_export"
)


# ==========================================================
# PROJECT LOOKUP
# ==========================================================

def build_project_lookup(projects):
    """
    Build an ID-to-project lookup.
    """

    return {
        project["id"]: project
        for project in projects
        if project.get("id")
    }


# ==========================================================
# PROCESS ONE PROJECT
# ==========================================================

def process_project(
    access_token,
    project,
):
    """
    Extract and save the Entity 3D User Field table
    for one project.

    Returns the output table.
    """

    project_id = project["id"]

    project_name = (
        project.get("displayName")
        or project.get("name")
        or project_id
    )

    project_label = build_project_label(
        project_name
    )

    print()
    print("=" * 80)
    print(
        f"PROCESSING PROJECT: {project_name}"
    )
    print(
        f"PROJECT ID: {project_id}"
    )
    print(
        f"PROJECT LABEL: {project_label}"
    )
    print("=" * 80)

    print()
    print(
        "*** Building tabulated Entity 3D "
        "User Field output..."
    )

    output_records = (
        get_project_entity_userfield_table(
            access_token=access_token,
            project_id=project_id,
            requested_userfield_names=(
                REQUESTED_USER_FIELD_NAMES
            ),
            schedule_index=SCHEDULE_INDEX,
        )
    )

    if not output_records:
        print(
            "*** No output records were returned "
            "for this project."
        )

        return []

    print(
        f"*** Tabulated output created "
        f"successfully: "
        f"{len(output_records)} rows"
    )

    print()
    print(
        f"*** Previewing first "
        f"{min(
            CONSOLE_PREVIEW_ROWS,
            len(output_records),
        )} output rows..."
    )

    print_records(
        output_records,
        n=CONSOLE_PREVIEW_ROWS,
    )

    prefixed_filename = (
        f"{project_label}_"
        f"{OUTPUT_FILENAME}"
    )

    output_file = compile_filename(
        uptree=1,
        destination=OUTPUT_DESTINATION,
        filename=prefixed_filename,
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

    return output_records


# ==========================================================
# MAIN
# ==========================================================

def main():
    print()
    print("*** Getting access token...")

    access_token = get_access_token()

    print(
        "*** Access token obtained successfully."
    )

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
        f"*** Project list obtained "
        f"successfully: {len(projects)}"
    )

    # ------------------------------------------------------
    # SELECT PROJECTS
    # ------------------------------------------------------

    selected_project_ids = select_projects(
        projects=projects,
        title="Select SYNCHRO projects",
    )

    if not selected_project_ids:
        print()
        print(
            "*** No projects selected. "
            "Nothing to process."
        )

        return

    print()
    print(
        f"*** Projects selected: "
        f"{len(selected_project_ids)}"
    )

    project_lookup = build_project_lookup(
        projects
    )

    successful_projects = []
    failed_projects = []

    # ------------------------------------------------------
    # PROCESS SELECTED PROJECTS
    # ------------------------------------------------------

    for project_id in selected_project_ids:
        project = project_lookup.get(
            project_id
        )

        if project is None:
            failed_projects.append(
                {
                    "project_id": project_id,
                    "project_name": "",
                    "error": (
                        "Selected project was not found "
                        "in the project response."
                    ),
                }
            )

            continue

        project_name = (
            project.get("displayName")
            or project.get("name")
            or project_id
        )

        try:
            output_records = process_project(
                access_token=access_token,
                project=project,
            )

            successful_projects.append(
                {
                    "project_id": project_id,
                    "project_name": project_name,
                    "row_count": len(output_records),
                }
            )

        except Exception as ex:
            failed_projects.append(
                {
                    "project_id": project_id,
                    "project_name": project_name,
                    "error": str(ex),
                }
            )

            print()
            print(
                f"ERROR processing "
                f"'{project_name}':"
            )
            print(str(ex))


    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------

    print()
    print("=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)

    print()
    print(
        f"Successful projects: "
        f"{len(successful_projects)}"
    )

    if successful_projects:
        print_records(
            successful_projects,
            n=len(successful_projects),
        )

    print(
        f"Failed projects: "
        f"{len(failed_projects)}"
    )

    if failed_projects:
        print_records(
            failed_projects,
            n=len(failed_projects),
        )

    print()
    print("*** Process completed.")


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()