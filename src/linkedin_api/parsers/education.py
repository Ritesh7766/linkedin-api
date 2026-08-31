import re

import requests

from linkedin_api.client import LinkedInClient
from linkedin_api.fetchers.section import fetch_profile_section
from linkedin_api.models import Education

_EDUCATION_COLLECTION = "EducationTopLevelSection"

_REFERENCE_RE = re.compile(
    r"\$L([0-9a-z]+)",
    re.IGNORECASE,
)

_DATE_RE = re.compile(r"^(?:\d{4}\s*[–-]\s*\d{4})$")


def _extract_definitions(
    data: str,
) -> dict[str, str]:
    return dict(
        re.findall(
            r"^([0-9a-z]+):(.+)$",
            data,
            re.MULTILINE | re.IGNORECASE,
        )
    )


def _resolve_refs(
    data: str,
    definitions: dict[str, str],
) -> str:
    def resolve(
        value: str,
        stack: frozenset[str] = frozenset(),
    ) -> str:
        def replace(
            match: re.Match[str],
        ) -> str:
            key = match.group(1)

            if key in stack:
                return ""

            definition = definitions.get(key)

            if definition is None:
                return match.group(0)

            return resolve(
                definition,
                stack | {key},
            )

        return _REFERENCE_RE.sub(
            replace,
            value,
        )

    return resolve(data)


def _get_text_children(
    data: str,
) -> list[str]:
    values: list[str] = []

    patterns = (
        r'"children":\["([^"]+)"\]',
        r'"children":\[(?:null,)+"([^"]+)"\]',
    )

    for pattern in patterns:
        values.extend(
            match.group(1).strip()
            for match in re.finditer(
                pattern,
                data,
            )
            if match.group(1).strip()
        )

    return values


def _is_date(
    value: str,
) -> bool:
    return bool(_DATE_RE.fullmatch(value))


def _parse_item(
    values: list[str],
) -> Education | None:
    date_index = next(
        (index for index, value in enumerate(values) if _is_date(value)),
        None,
    )

    if date_index is None or date_index < 2:
        return None

    school = values[date_index - 2]

    degree_field = values[date_index - 1]

    if "," in degree_field:
        degree, field_of_study = degree_field.split(
            ",",
            1,
        )
    else:
        degree = degree_field
        field_of_study = None

    return Education(
        school=school,
        degree=degree.strip() if degree else None,
        field_of_study=(field_of_study.strip() if field_of_study else None),
        dates=values[date_index],
    )


def parse_education(
    data: str,
) -> list[Education]:
    """
    Parse education entries from a LinkedIn profile section.

    Parameters
    ----------
    data : str
        Raw LinkedIn profile section response.

    Returns
    -------
    list[Education]
        Parsed education entries.
    """

    definitions = _extract_definitions(data)

    collection_key = next(
        (key for key, value in definitions.items() if _EDUCATION_COLLECTION in value),
        None,
    )

    if collection_key is None:
        return []

    collection = _resolve_refs(
        definitions[collection_key],
        definitions,
    )

    item_matches = list(
        re.finditer(
            r'"key":"(entity-collection-item-[^"]+)"',
            collection,
        )
    )

    education: list[Education] = []

    for index, match in enumerate(item_matches):
        start = match.start()

        end = (
            item_matches[index + 1].start()
            if index + 1 < len(item_matches)
            else len(collection)
        )

        resolved_item = _resolve_refs(
            collection[start:end],
            definitions,
        )

        values = _get_text_children(
            resolved_item,
        )

        values = [
            value
            for index, value in enumerate(values)
            if index == 0 or value != values[index - 1]
        ]

        parsed = _parse_item(values)

        if parsed is not None:
            education.append(parsed)

    return education


def get_education(
    client: LinkedInClient,
    vanity_name: str,
    profile_id: str | None,
) -> list[Education]:
    """
    Fetch and parse LinkedIn education information.

    Parameters
    ----------
    client : LinkedInClient
        Authenticated LinkedIn client.

    vanity_name : str
        LinkedIn profile vanity name.

    profile_id : str or None
        LinkedIn profile ID.

    Returns
    -------
    list[Education]
        Parsed education entries.
    """

    if not profile_id:
        return []

    for part in range(1, 11):
        try:
            data = fetch_profile_section(
                client,
                vanity_name,
                profile_id,
                part,
            )
        except requests.RequestException:
            continue

        education = parse_education(data)

        if education:
            return education

    return []
