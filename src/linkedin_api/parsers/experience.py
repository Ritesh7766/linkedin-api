import re
from typing import cast

from linkedin_api.client import LinkedInClient
from linkedin_api.fetchers.experience import fetch_experience
from linkedin_api.models import Experience

_MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"

_DATE_RE = re.compile(
    rf"^{_MONTH}\s+\d{{4}}"
    rf"\s*-\s*"
    rf"(?:Present|{_MONTH}\s+\d{{4}})"
    rf"(?:\s*·\s*.+)?$"
)

_LOCATION_RE = re.compile(r"^.+\s·\s(?:On-site|Remote|Hybrid)$")

_DURATION_RE = re.compile(
    r"^\d+\s+(?:yr|yrs|mo|mos)" r"(?:\s+\d+\s+(?:yr|yrs|mo|mos))?$"
)

_EMPLOYMENT_TYPES = {
    "Full-time",
    "Part-time",
    "Contract",
    "Temporary",
    "Volunteer",
    "Internship",
    "Apprenticeship",
    "Freelance",
    "Self-employed",
}


def _extract_definitions(
    data: str,
) -> dict[str, str]:
    return dict(
        re.findall(
            r"^([0-9a-z]+):(.*)$",
            data,
            re.MULTILINE | re.IGNORECASE,
        )
    )


def _resolve_refs(
    data: str,
    definitions: dict[str, str],
) -> str:
    reference_re = re.compile(
        r"\$L([0-9a-z]+)",
        re.IGNORECASE,
    )

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

        return reference_re.sub(
            replace,
            value,
        )

    return resolve(data)


def _get_text_children(
    data: str,
) -> list[str]:
    values: list[str] = []

    patterns = (
        r'"children":\["([^"]*)"\]',
        r'"children":\[(?:null,)+"([^"]*)"\]',
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


def _is_date(value: str) -> bool:
    return bool(_DATE_RE.fullmatch(value))


def _is_location(value: str) -> bool:
    return bool(_LOCATION_RE.fullmatch(value))


def _is_duration(value: str) -> bool:
    return bool(_DURATION_RE.fullmatch(value))


def _is_employment(value: str) -> bool:
    return value in _EMPLOYMENT_TYPES


def _split_company(
    value: str,
) -> tuple[str, str | None]:
    if " · " not in value:
        return value, None

    company, employment_type = value.split(
        " · ",
        1,
    )

    return company.strip(), employment_type.strip()


def _parse_item(
    values: list[str],
) -> list[Experience]:
    date_indices = [index for index, value in enumerate(values) if _is_date(value)]

    if not date_indices:
        return []

    # Single position:
    #
    # Title
    # Company · Employment
    # Dates
    # Location

    if len(date_indices) == 1:
        date_index = date_indices[0]

        if date_index < 2:
            return []

        company, employment_type = _split_company(values[date_index - 1])

        title = cast(str, values[date_index - 2])

        location = None

        if date_index + 1 < len(values):
            candidate = values[date_index + 1]

            if _is_location(candidate):
                location = candidate

        return [
            Experience(
                company=company,
                title=title,
                employment_type=employment_type,
                dates=values[date_index],
                location=location,
            )
        ]

    # Multiple positions at one company.

    company = values[0]
    cursor = 1

    company_employment = None
    company_duration = None
    company_location = None

    if cursor < len(values):
        metadata = values[cursor]

        if " · " in metadata and not _is_date(metadata) and not _is_location(metadata):
            employment, duration = metadata.split(
                " · ",
                1,
            )

            if _is_employment(employment):
                company_employment = employment
                company_duration = duration
                cursor += 1

        elif _is_duration(metadata):
            company_duration = metadata
            cursor += 1

    if cursor < len(values) and _is_location(values[cursor]):
        company_location = values[cursor]
        cursor += 1

    position_values = values[cursor:]

    position_dates = [
        index for index, value in enumerate(position_values) if _is_date(value)
    ]

    experiences: list[Experience] = []

    for date_index in position_dates:
        title = ""
        employment_type = company_employment
        location = company_location

        if date_index > 0:
            previous = position_values[date_index - 1]

            if _is_employment(previous):
                employment_type = previous

                if date_index > 1:
                    title = position_values[date_index - 2]
            else:
                title = previous

        if date_index + 1 < len(position_values):
            candidate = position_values[date_index + 1]

            if _is_location(candidate):
                location = candidate

        if not title:
            continue

        if _is_date(title) or _is_location(title) or _is_duration(title):
            continue

        experiences.append(
            Experience(
                company=company,
                title=title,
                employment_type=employment_type,
                dates=position_values[date_index],
                location=location,
                company_duration=company_duration,
            )
        )

    return experiences


def parse_experience(
    data: str,
) -> list[Experience]:
    """
    Parse work experience from a raw LinkedIn Experience response.

    Parameters
    ----------
    data : str
        Raw response returned by the LinkedIn Experience component.

    Returns
    -------
    list[Experience]
        Parsed work experience entries.
    """

    definitions = _extract_definitions(data)

    collection_key = next(
        (
            key
            for key, value in definitions.items()
            if '"collectionId":"profile_ExperienceTopLevelSection_' in value
        ),
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

    experiences: list[Experience] = []

    for index, match in enumerate(item_matches):
        start = match.start()

        end = (
            item_matches[index + 1].start()
            if index + 1 < len(item_matches)
            else len(collection)
        )

        item = collection[start:end]

        resolved_item = _resolve_refs(
            item,
            definitions,
        )

        values = _get_text_children(resolved_item)

        values = [
            value
            for index, value in enumerate(values)
            if index == 0 or value != values[index - 1]
        ]

        values = [value for value in values if value not in {"Experience", "Show all"}]

        experiences.extend(_parse_item(values))

    return experiences


def get_experience(
    client: LinkedInClient,
    vanity_name: str,
    profile_id: str,
) -> list[Experience]:
    """
    Fetch and parse LinkedIn work experience.

    Parameters
    ----------
    client : LinkedInClient
        Authenticated LinkedIn client used to fetch the experience.
    vanity_name : str
        Vanity name of the LinkedIn profile.
    profile_id : str
        LinkedIn profile ID required by the Experience component.

    Returns
    -------
    list[Experience]
        Parsed work experience entries.
    """
    return parse_experience(
        fetch_experience(
            client,
            vanity_name,
            profile_id,
        )
    )
