from linkedin_api.models import Skill
from linkedin_api.parsers.common import (
    extract_text,
    get_collection,
    get_collection_items,
)


_SKILLS_COLLECTION = "SkillsTopLevelSection"

_NOISE = {"Skills", "Show all"}


def parse_skills(data: str) -> list[Skill]:
    """
    Parse skills from one raw LinkedIn profile section response.
    """

    result = get_collection(data, _SKILLS_COLLECTION)

    if result is None:
        return []

    collection, definitions = result
    skills: list[Skill] = []
    seen: set[str] = set()

    for item in get_collection_items(collection, definitions):
        for value in extract_text(item):
            if value in _NOISE:
                continue

            if value not in seen:
                seen.add(value)
                skills.append(Skill(name=value))

            # Each collection item's first useful text node is the skill
            # name; later nodes are endorsements/sub-labels - skip them.
            break

    return skills
