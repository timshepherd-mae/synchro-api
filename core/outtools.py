import json
import re
from pathlib import Path


# ==========================================================
# CONSTANTS
# ==========================================================

FILETYPE_CSV = 0
FILETYPE_TSV = 1

# ==========================================================
# PROJECT LABEL
# ==========================================================

def build_project_label(
    project_name,
    length=6,
):
    """
    Build a compact uppercase project label.

    Processing:
        1. Convert the name to text.
        2. Remove all whitespace.
        3. Take the first `length` characters.
        4. Convert to uppercase.
        5. Replace Windows-invalid filename characters.

    Examples
    --------
    "Yorkshire Green" -> "YORKSH"

    "Project Alpha" -> "PROJEC"
    """

    compact_name = re.sub(
        r"\s+",
        "",
        str(project_name),
    )

    project_label = (
        compact_name[:length]
        .upper()
    )

    project_label = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        project_label,
    )

    return project_label or "PROJCT"



# ==========================================================
# FILENAME COMPILER
# ==========================================================

def compile_filename(
    uptree: int = 0,
    destination: str = "data_export",
    filename: str = "output"
):

    script_folder = Path(__file__).resolve().parent
    folder = script_folder

    for _ in range(uptree + 1):
        folder = folder.parent

    destination_folder = folder / destination
    output_file = destination_folder / filename

    return output_file


# ==========================================================
# FILE OUTPUT
# ==========================================================

def save_response_records(
    records,
    filename,
    filetype=0
):
    """
    Save a list of response dictionaries as CSV or TSV.

    Parameters
    ----------
    records : list[dict]
        API response records.

    filename : str
        Filename WITHOUT extension.

    filetype : int
        0 = CSV
        1 = TSV

    Returns
    -------
    str
        Full filename written.
    """

    delimiter = "," if filetype == 0 else "\t"
    extension = ".csv" if filetype == 0 else ".tsv"

    # filepath = filename + extension
    filepath = Path(filename).with_suffix(extension)


    if not records:

        with open(filepath, "w", encoding="utf-8") as f:
            pass

        return filepath

    # Collect all available fields
    fields = sorted(
        {
            key
            for row in records
            for key in row.keys()
        }
    )

    with open(
        filepath,
        "w",
        encoding="utf-8-sig"
    ) as f:

        # Header
        f.write(
            delimiter.join(fields) + "\n"
        )

        # Data rows
        for row in records:

            values = []

            for field in fields:

                value = row.get(field, "")

                if value is None:
                    value = ""

                value = (
                    str(value)
                    .replace("\r", " ")
                    .replace("\n", " ")
                )

                values.append(value)

            f.write(
                delimiter.join(values) + "\n"
            )

    return filepath


# ==========================================================
# CONSOLE OUTPUT
# ==========================================================


def print_records(records, n=50, padding=1):
    """
    Print a list of record dictionaries as a table.
    """

    if not isinstance(records, list):
        raise TypeError(
            "print_records() expects a list of dictionaries, "
            f"but received {type(records).__name__}."
        )

    if not records:
        print("[EMPTY LIST]")
        return

    if not all(
        isinstance(record, dict)
        for record in records
    ):
        raise TypeError(
            "print_records() expects every list item "
            "to be a dictionary."
        )

    if n == 0:
        return

    for _ in range(padding):
        print()

    rows = records[:n] if n > 0 else records[n:]

    # Continue with the existing function...
    # Build field list
    fields = []

    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)

    # Determine column widths
    widths = {}

    for field in fields:

        max_width = len(str(field))

        for row in rows:
            value = str(row.get(field, ""))
            max_width = max(max_width, len(value))

        widths[field] = min(max_width, 50)

    # Header
    header = " | ".join(
        field.ljust(widths[field])
        for field in fields
    )

    print(header)
    print("-" * len(header))

    # Rows
    for row in rows:

        line = " | ".join(
            str(row.get(field, ""))[:50].ljust(widths[field])
            for field in fields
        )

        print(line)

    print(
        f"\nDisplayed {len(rows)} of {len(records)} records"
    )

    # print bottom padding
    for _ in range(padding):
        print()    


def print_first(items, title="FIRST ITEM"):
    """
    Print the first item of a list.
    Returns nothing.
    """

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    if not items:
        print("[EMPTY LIST]")
        return

    print(json.dumps(
        items[0],
        indent=4,
        default=str
    ))


def print_last(items, title="LAST ITEM"):
    """
    Print the last item of a list.
    Returns nothing.
    """

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    if not items:
        print("[EMPTY LIST]")
        return

    print(json.dumps(
        items[-1],
        indent=4,
        default=str
    ))