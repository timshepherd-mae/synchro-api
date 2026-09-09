

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
# LOCAL HELPER FUNCTIONS
# ==========================================================

def get_first_value(record, keys, default=None):
    """
    Return the first non-None value found for the supplied keys.

    This allows the script to tolerate minor differences in API
    property naming, such as:

        id
        entityId
        entity3dId
        userFieldId
        userfieldId
    """

    if not isinstance(record, dict):
        return default

    for key in keys:
        if key in record and record[key] is not None:
            return record[key]

    return default

def normalise_name(value):
    """
    Normalise a name for case-insensitive matching.
    """

    if value is None:
        return ""

    return str(value).strip().casefold()

def get_userfield_id(user_field):
    """
    Extract the User Field ID from a User Field definition.
    """

    return get_first_value(
        user_field,
        [
            "id",
            "userFieldId",
            "userfieldId",
        ],
    )

def get_userfield_name(user_field):
    """
    Extract the User Field name from a User Field definition.
    """

    return get_first_value(
        user_field,
        [
            "name",
            "displayName",
            "label",
        ],
    )

def get_entity_id(entity):
    """
    Extract the Entity 3D ID from an Entity 3D record.
    """

    return get_first_value(
        entity,
        [
            "id",
            "entityId",
            "entity3dId",
            "entity3DId",
        ],
    )

def get_value_record_entity_id(value_record):
    """
    Extract the Entity 3D ID from a User Field value record.
    """

    entity_id = get_first_value(
        value_record,
        [
            "entityId",
            "entity3dId",
            "entity3DId",
            "objectId",
        ],
    )

    if entity_id is not None:
        return entity_id

    nested_entity = get_first_value(
        value_record,
        [
            "entity",
            "entity3d",
            "entity3D",
        ],
    )

    if isinstance(nested_entity, dict):
        return get_entity_id(nested_entity)

    return None

def get_value_record_userfield_id(value_record):
    """
    Extract the User Field ID from a User Field value record.
    """

    user_field_id = get_first_value(
        value_record,
        [
            "userFieldId",
            "userfieldId",
            "fieldId",
        ],
    )

    if user_field_id is not None:
        return user_field_id

    nested_user_field = get_first_value(
        value_record,
        [
            "userField",
            "userfield",
            "field",
        ],
    )

    if isinstance(nested_user_field, dict):
        return get_userfield_id(nested_user_field)

    return None

def get_value_record_value(value_record):
    """
    Extract the actual value from a User Field value record.
    """

    value = get_first_value(
        value_record,
        [
            "value",
            "displayValue",
            "textValue",
            "stringValue",
            "numberValue",
            "dateValue",
            "booleanValue",
        ],
    )

    if isinstance(value, dict):
        nested_value = get_first_value(
            value,
            [
                "value",
                "displayValue",
                "text",
                "name",
            ],
        )

        if nested_value is not None:
            return nested_value

    if value is None:
        return ""

    return value

def flatten_userfield_value_records(records):
    """
    Flatten User Field value responses where values may be stored as:

        one record per entity/User Field combination

    or:

        one entity record containing a list named:
            userFieldValues
            userfieldValues
            values
    """

    flattened_records = []

    for record in records:
        if not isinstance(record, dict):
            continue

        nested_values = get_first_value(
            record,
            [
                "userFieldValues",
                "userfieldValues",
                "fieldValues",
                "values",
            ],
        )

        if not isinstance(nested_values, list):
            flattened_records.append(record)
            continue

        parent_entity_id = get_value_record_entity_id(record)

        if parent_entity_id is None:
            parent_entity_id = get_entity_id(record)

        for nested_value in nested_values:
            if not isinstance(nested_value, dict):
                continue

            flattened_value = dict(nested_value)

            if (
                get_value_record_entity_id(flattened_value)
                is None
            ):
                flattened_value["entityId"] = parent_entity_id

            flattened_records.append(flattened_value)

    return flattened_records

