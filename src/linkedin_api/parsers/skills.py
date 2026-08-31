from linkedin_api.client.client import LinkedInClient
from linkedin_api.fetchers.skills import fetch_skills
from linkedin_api.models import Skill
from linkedin_api.parsers.common import (
    extract_text,
    get_collection,
    get_collection_items,
)

_SKILLS_COLLECTION = "SkillDetails"


def parse_skills(data: str) -> list[Skill]:
    """
    Parse skill names from a raw LinkedIn Skills RSC response.

    Parameters
    ----------
    data : str
        Raw RSC response returned by LinkedIn's Skills details
        endpoint.

    Returns
    -------
    list[Skill]
        Parsed LinkedIn profile skills.
    """
    result = get_collection(
        data,
        _SKILLS_COLLECTION,
    )

    if result is None:
        return []

    collection, definitions = result
    items = get_collection_items(collection, definitions)

    skills: list[Skill] = []

    for item in items:
        values = extract_text(item)

        if not values:
            continue

        skills.append(
            Skill(
                name=values[0],
            )
        )

    return skills


def get_skills(
    client: LinkedInClient,
    vanity_name: str,
) -> list[Skill]:
    """
    Fetch and parse skills for a LinkedIn profile.

    Parameters
    ----------
    client : LinkedInClient
        Authenticated LinkedIn client used to make the request.

    vanity_name : str
        Vanity name of the LinkedIn profile.

    Returns
    -------
    list[Skill]
        Parsed skills returned by LinkedIn.
    """
    data = fetch_skills(
        client=client,
        vanity_name=vanity_name,
    )

    return parse_skills(data)
