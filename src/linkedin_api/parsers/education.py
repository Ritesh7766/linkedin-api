import re

from linkedin_api.models import Education
from linkedin_api.parsers.common import (
    extract_text,
    get_collection,
    get_collection_items,
)

_EDUCATION_COLLECTION = (
    "profile_EducationTopLevelSection_",
    "EducationTopLevelSection",
)

# Accepts "2020-2024", "Mar 2026 - Mar 2029", "Aug 2024 - Present", etc.
# The original pattern only matched bare "YYYY-YYYY" ranges and silently
# failed to recognise month-qualified ranges (LinkedIn uses both formats).
_DATE_RE = re.compile(
    r"^(?:[A-Za-z]{3,9}\.?\s+)?\d{4}\s*[–-]\s*"
    r"(?:(?:[A-Za-z]{3,9}\.?\s+)?\d{4}|Present)$"
)

_NOISE_PREFIXES = ("Show all", "Show credential", "GitHub -")
_NOISE = {"Transcript"}


def _is_date(value: str) -> bool:
    return bool(_DATE_RE.fullmatch(value))


def _is_noise(value: str) -> bool:
    return value in _NOISE or value.startswith(_NOISE_PREFIXES)


def _parse_item(values: list[str]) -> Education | None:
    date_index = next(
        (index for index, value in enumerate(values) if _is_date(value)),
        None,
    )

    if date_index is None or date_index < 2:
        return None

    school = values[date_index - 2]
    degree_field = values[date_index - 1]

    if "," in degree_field:
        degree, field_of_study = degree_field.split(",", 1)
    else:
        degree, field_of_study = degree_field, None

    grade: str | None = None
    description_parts: list[str] = []

    for value in values[date_index + 1 :]:
        if _is_noise(value):
            continue

        if value.lower().startswith("grade"):
            grade = value.split(":", 1)[-1].strip() if ":" in value else value
            continue

        description_parts.append(value)

    return Education(
        school=school,
        degree=degree.strip() if degree else None,
        field_of_study=field_of_study.strip() if field_of_study else None,
        dates=values[date_index],
        grade=grade,
        description=" ".join(description_parts) or None,
    )


def parse_education(data: str) -> list[Education]:
    """
    Parse education entries from one raw LinkedIn profile section response.
    """

    result = get_collection(data, _EDUCATION_COLLECTION)

    if result is None:
        return []

    collection, definitions = result
    education: list[Education] = []

    for item in get_collection_items(collection, definitions):
        values = extract_text(item)

        # Collapse consecutive duplicate text nodes (LinkedIn renders some
        # labels twice - once visually hidden - for accessibility).
        values = [
            value
            for index, value in enumerate(values)
            if index == 0 or value != values[index - 1]
        ]

        parsed = _parse_item(values)

        if parsed is not None:
            education.append(parsed)

    return education
