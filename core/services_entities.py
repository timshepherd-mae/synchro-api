from core.api_schedules import get_schedules

from core.api_userfields import (
    get_all_userfields,
)

from core.api_entities import (
    get_all_entities,
    get_all_entity_userfield_values,
)

from core.data_userfields import (
    resolve_entity_userfields,
    build_entity_userfield_table,
)

def get_entity_userfield_table(
    access_token,
    project_id,
    requested_userfield_names,
):
    schedules = get_schedules(
        access_token,
        project_id,
    )["schedules"]

    schedule = schedules[schedule_index]

    schedule_id = schedule["id"]

    user_fields = get_all_userfields(
        access_token,
        schedule_id,
    )

    selected_user_fields = (
        resolve_entity_userfields(
            user_fields,
            requested_userfield_names,
        )
    )

    entities = get_all_entities(
        access_token,
        schedule_id,
    )

    values = (
        get_all_entity_userfield_values(
            access_token,
            schedule_id,
        )
    )

    output_records = (
        build_entity_userfield_table(
            entities,
            values,
            selected_user_fields,
        )
    )

    return output_records
