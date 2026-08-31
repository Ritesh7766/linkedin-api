import re

from linkedin_api.models import Skill


SKILLS_COLLECTION = "SkillsTopLevelSection"

REFERENCE_RE = re.compile(
    r"\$L([0-9a-z]+)",
    re.IGNORECASE,
)


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

        return REFERENCE_RE.sub(
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


def parse_skills(
    data: str,
) -> list[Skill]:
    """
    Parse skills from raw LinkedIn section data.
    """

    definitions = _extract_definitions(data)

    collection_key = next(
        (key for key, value in definitions.items() if SKILLS_COLLECTION in value),
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

    skills: list[Skill] = []
    seen: set[str] = set()

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

        for value in values:
            if value in {
                "Skills",
                "Show all",
                "Visible",
                "Collapsed",
                "Expanded",
            }:
                continue

            if value not in seen:
                seen.add(value)
                skills.append(Skill(name=value))

            break

    return skills
