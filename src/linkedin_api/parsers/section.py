from collections.abc import Callable
from typing import Any

import requests

from linkedin_api.client import LinkedInClient
from linkedin_api.fetchers.section import fetch_profile_section
from linkedin_api.models import Education, Skill
from linkedin_api.parsers.education import parse_education
from linkedin_api.parsers.skills import parse_skills


SectionParser = Callable[[str], list[Any]]


# One literal RSC component-name substring per section. LinkedIn's payload
# for a given "part" carries these as plain strings, so a substring check
# against the raw (pre-resolution) text is enough to know a part is worth
# handing to that section's parser.
SECTION_IDENTIFIERS: dict[str, tuple[str, ...]] = {
    "education": ("EducationTopLevelSection",),
    "skills": ("SkillsTopLevelSection",),
}

SECTION_PARSERS: dict[str, SectionParser] = {
    "education": parse_education,
    "skills": parse_skills,
}


def _detect_sections(data: str, remaining: set[str]) -> list[str]:
    """
    Return every outstanding section whose identifier appears in `data`.

    A single part's payload can legitimately carry more than one section's
    data (LinkedIn bundles sibling section stubs together) - so this must
    return *all* matches, not just the first. Returning only the first
    match is what silently starved every section but the first one to
    match in a given run.
    """

    return [
        section
        for section in remaining
        if any(identifier in data for identifier in SECTION_IDENTIFIERS[section])
    ]


def get_parsed_sections(
    client: LinkedInClient,
    vanity_name: str,
    profile_id: str | None,
    *,
    max_parts: int = 10,
) -> tuple[list[Education], list[Skill]]:
    """
    Fetch and parse every registered section, one shared pass over parts.

    Correctness matches the original per-section loop in `main` (every
    part up to `max_parts` is tried, for every section, until found).
    Efficiency comes from fetching each part exactly once and checking it
    against every section still outstanding, instead of re-fetching the
    same parts once per section - and from stopping as soon as nothing is
    left to find.
    """

    results: dict[str, list[Any]] = {name: [] for name in SECTION_PARSERS}

    if not profile_id:
        return results["education"], results["skills"]

    remaining = set(SECTION_PARSERS)

    for part in range(1, max_parts + 1):
        if not remaining:
            break

        try:
            data = fetch_profile_section(client, vanity_name, profile_id, part)
        except requests.RequestException:
            continue

        if not data or not data.strip():
            continue

        for section in _detect_sections(data, remaining):
            parsed = SECTION_PARSERS[section](data)

            if not parsed:
                continue

            results[section] = parsed
            remaining.discard(section)

    return results["education"], results["skills"]
