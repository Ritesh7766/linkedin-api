import re

from linkedin_api.client.client import LinkedInClient
from linkedin_api.fetchers.experience import fetch_experience
from linkedin_api.models import Experience
from linkedin_api.parsers.common import (
    extract_text,
    get_collection,
    get_collection_items,
)


_EXPERIENCE_COLLECTION = "ExperienceDetailsSection"

_DATE_RE = re.compile(
    r"""
    ^
    (?P<dates>.+?)
    \s*·\s*
    (?P<duration>
        \d+\s+(?:yr|yrs|mo|mos)
        (?:\s+\d+\s+(?:yr|yrs|mo|mos))?
    )
    $
    """,
    re.VERBOSE,
)


def _parse_date_info(value: str) -> tuple[str, str | None]:
    """Split a LinkedIn date string into its date range and duration."""
    match = _DATE_RE.match(value)

    if match is None:
        return value, None

    return match.group("dates"), match.group("duration")


def _parse_company(value: str) -> tuple[str, str | None]:
    """Split a LinkedIn company string into name and employment type."""
    company, separator, employment_type = value.partition(" · ")

    if not separator:
        return value, None

    return company, employment_type


def parse_experience(data: str) -> list[Experience]:
    """
    Parse a raw LinkedIn Experience details RSC response.

    Parameters
    ----------
    data : str
        Raw RSC response returned by LinkedIn's Experience details
        endpoint.

    Returns
    -------
    list[Experience]
        Parsed LinkedIn work experience entries. Returns an empty
        list when the Experience collection is not present.
    """
    result = get_collection(data, _EXPERIENCE_COLLECTION)

    if result is None:
        return []

    collection, definitions = result
    items = get_collection_items(collection, definitions)

    experiences: list[Experience] = []

    for item in items:
        values = extract_text(item)

        if len(values) < 2:
            continue

        title = values[0]
        company, employment_type = _parse_company(values[1])

        dates = None
        company_duration = None
        location = None

        if len(values) > 2:
            dates, company_duration = _parse_date_info(values[2])

        if len(values) > 3:
            location = values[3]

        experiences.append(
            Experience(
                title=title,
                company=company,
                employment_type=employment_type,
                dates=dates,
                location=location,
                company_duration=company_duration,
            )
        )

    return experiences


def get_experience(
    client: LinkedInClient,
    vanity_name: str,
) -> list[Experience]:
    """
    Fetch and parse work experience for a LinkedIn profile.

    Parameters
    ----------
    client : LinkedInClient
        Authenticated LinkedIn client used to make the request.

    vanity_name : str
        Vanity name of the LinkedIn profile.

    Returns
    -------
    list[Experience]
        Parsed work experience entries for the profile.
    """
    return parse_experience(
        fetch_experience(
            client=client,
            vanity_name=vanity_name,
        )
    )
