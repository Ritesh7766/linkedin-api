from collections.abc import Callable
from typing import Any

import requests

from linkedin_api.client import LinkedInClient
from linkedin_api.fetchers.section import fetch_profile_section
from linkedin_api.models import Education, Skill
from linkedin_api.parsers.education import parse_education
from linkedin_api.parsers.skills import parse_skills


SectionParser = Callable[[str], list[Any]]


SECTION_IDENTIFIERS = {
    "education": ("EducationTopLevelSection",),
    "skills": ("SkillsTopLevelSection",),
}


SECTION_PARSERS: dict[str, SectionParser] = {
    "education": parse_education,
    "skills": parse_skills,
}


def _detect_section(
    data: str,
    remaining: set[str],
) -> str | None:
    for section in remaining:
        identifiers = SECTION_IDENTIFIERS[section]

        if any(identifier in data for identifier in identifiers):
            return section

    return None


def get_parsed_sections(
    client: LinkedInClient,
    vanity_name: str,
    profile_id: str | None,
    *,
    max_parts: int = 10,
) -> tuple[list[Education], list[Skill]]:

    education: list[Education] = []
    skills: list[Skill] = []

    results: dict[str, list[Any]] = {
        "education": education,
        "skills": skills,
    }

    if not profile_id:
        return education, skills

    remaining = set(SECTION_PARSERS)

    for part in range(1, max_parts + 1):
        if not remaining:
            break

        try:
            data = fetch_profile_section(
                client,
                vanity_name,
                profile_id,
                part,
            )
        except requests.RequestException:
            continue

        if not data or not data.strip():
            continue

        section = _detect_section(
            data,
            remaining,
        )

        if section is None:
            continue

        parser = SECTION_PARSERS[section]

        # Pass the COMPLETE RAW RESPONSE.
        parsed = parser(data)

        if not parsed:
            continue

        results[section] = parsed
        remaining.remove(section)

    return (
        results["education"],
        results["skills"],
    )
