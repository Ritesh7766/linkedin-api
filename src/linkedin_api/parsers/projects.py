from linkedin_api.models import Project
from linkedin_api.parsers.common import (
    extract_target_url,
    extract_text,
    get_collection,
    get_collection_items,
)

_PROJECTS_COLLECTION = (
    "profile_Projects_",
    "com.linkedin.sdui.impl.profile.components.projectsSection",
)

_NOISE_PREFIXES = ("Show all", "GitHub -")


def _is_noise(value: str) -> bool:
    return value.startswith(_NOISE_PREFIXES)


def _parse_item(item: str) -> Project | None:
    values = [value for value in extract_text(item) if value and not _is_noise(value)]

    values = [
        value
        for index, value in enumerate(values)
        if index == 0 or value != values[index - 1]
    ]

    if not values:
        return None

    name = values[0]
    description = " ".join(values[1:]).strip() or None

    return Project(
        name=name,
        description=description,
        url=extract_target_url(item),
    )


def parse_projects(data: str) -> list[Project]:
    """
    Parse projects from one raw LinkedIn profile section response.
    """

    result = get_collection(data, _PROJECTS_COLLECTION)

    if result is None:
        return []

    collection, definitions = result
    projects: list[Project] = []

    for item in get_collection_items(collection, definitions):
        parsed = _parse_item(item)

        if parsed is not None:
            projects.append(parsed)

    return projects
