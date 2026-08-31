from collections.abc import Callable
from typing import Any

import requests

from linkedin_api.client import LinkedInClient
from linkedin_api.fetchers.section import fetch_profile_section
from linkedin_api.parsers.certifications import parse_certifications
from linkedin_api.parsers.education import parse_education
from linkedin_api.parsers.projects import parse_projects
from linkedin_api.parsers.skills import parse_skills

SectionParser = Callable[[str], list[Any]]


# Each section lists every candidate substring known to identify it in a raw
# response - the stable `collectionId`-style prefix where confirmed, plus
# the older component-key style as a fallback. Matched case-insensitively.
SECTION_IDENTIFIERS: dict[str, tuple[str, ...]] = {
    "education": ("profile_EducationTopLevelSection_", "EducationTopLevelSection"),
    "skills": ("profile_SkillsTopLevelSection_", "SkillsTopLevelSection"),
    "certifications": ("profile_CertificationTopLevel_", "CertificationTopLevel"),
    "projects": (
        "profile_Projects_",
        "com.linkedin.sdui.impl.profile.components.projectsSection",
    ),
}

SECTION_PARSERS: dict[str, SectionParser] = {
    "education": parse_education,
    "skills": parse_skills,
    "certifications": parse_certifications,
    "projects": parse_projects,
}


def _detect_sections(data: str, remaining: set[str]) -> list[str]:
    """
    Return every outstanding section whose identifier appears in `data`.

    A single part's payload can legitimately carry more than one section's
    data (LinkedIn bundles sibling section stubs together - confirmed: a
    single "part" response contained Education, Certifications and Projects
    at once) - so this must return *all* matches, not just the first.
    """

    lowered = data.lower()

    return [
        section
        for section in remaining
        if any(
            identifier.lower() in lowered for identifier in SECTION_IDENTIFIERS[section]
        )
    ]


def get_parsed_sections(
    client: LinkedInClient,
    vanity_name: str,
    profile_id: str | None,
    *,
    max_parts: int = 10,
) -> dict[str, list[Any]]:
    """
    Fetch and parse every registered section, one shared pass over parts.

    Returns a dict keyed by section name (e.g. "education", "skills",
    "certifications", "projects") rather than a positional tuple, so adding
    a section only means one new entry in SECTION_IDENTIFIERS/
    SECTION_PARSERS - no signature change here or in callers beyond
    indexing the new key.

    Correctness matches the original per-section loop in `main` (every
    part up to `max_parts` is tried, for every section, until found).
    Efficiency comes from fetching each part exactly once and checking it
    against every section still outstanding, instead of re-fetching the
    same parts once per section - and from stopping as soon as nothing is
    left to find.
    """

    results: dict[str, list[Any]] = {name: [] for name in SECTION_PARSERS}

    if not profile_id:
        return results

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

    return results
