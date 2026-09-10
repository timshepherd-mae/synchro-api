

# ==========================================================
# RESOLVE ENTITY 3D USER FIELDS BY NAME
# ==========================================================

def resolve_entity_userfields(
    user_fields,
    requested_names,
    allow_missing=False,
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

    if missing_names and not allow_missing:
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

        if not resolved_user_fields:
            raise ValueError(
                "None of the requested User Fields "
                "were found."
            )

    return resolved_user_fields


# ==========================================================
# BUILD ENTITY 3D USER FIELD TABLE
# ==========================================================

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

