import json
import re
from urllib.parse import parse_qs, unquote, urlparse

_REFERENCE_RE = re.compile(
    r"\$L([0-9a-z]+)",
    re.IGNORECASE,
)

_TEXT_PATTERNS = (
    # "children":["text"]
    re.compile(r'"children":\["([^"]*)"\]'),
    # "children":[null,...,"text"]
    re.compile(r'"children":\[(?:null,)+"([^"]*)"\]'),
    # "children":[[...one flat bracketed element, e.g. a <br>...],"text"]
    # Covers every paragraph after the first in a multi-fragment text block,
    # which the two patterns above silently drop (they require a plain
    # string or "null" immediately before the target string).
    re.compile(r'"children":\[\[[^\[\]]*\],"([^"]*)"\]'),
)

_NOISE = {
    "",
    "undefined",
    "$undefined",
    "Visible",
    "Collapsed",
    "Expanded",
}

_TARGET_URL_RE = re.compile(r'"urlValue":\{"\$case":"url","url":"([^"]+)"')


def extract_definitions(
    data: str,
) -> dict[str, str]:
    """
    Extract React Server Component definitions.
    """

    definitions: dict[str, str] = {}

    for line in data.splitlines():
        match = re.match(
            r"^([0-9a-z]+):(.+)$",
            line,
            re.IGNORECASE,
        )

        if match is not None:
            definitions[match.group(1)] = match.group(2)

    return definitions


def resolve_refs(
    value: str,
    definitions: dict[str, str],
) -> str:
    """
    Resolve RSC references recursively.
    """

    def resolve(
        current: str,
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

        previous = None

        while current != previous:
            previous = current
            current = _REFERENCE_RE.sub(
                replace,
                current,
            )

        return current

    return resolve(value)


def extract_text(
    data: str,
) -> list[str]:
    """
    Extract useful human-readable text while preserving true document order.

    Matches from all text-shape patterns are collected with their offset in
    `data` and then sorted by that offset, rather than concatenating each
    pattern's matches in turn - the latter silently reorders text whenever
    more than one shape appears in the same block (it did, here).
    """

    matches: list[tuple[int, str]] = []

    for pattern in _TEXT_PATTERNS:
        for match in pattern.finditer(data):
            matches.append((match.start(), match.group(1)))

    matches.sort(key=lambda pair: pair[0])

    values: list[str] = []
    seen: set[str] = set()

    for _, value in matches:
        try:
            value = json.loads(f'"{value}"')
        except json.JSONDecodeError:
            pass

        value = value.strip()

        if _is_noise(value) or value in seen:
            continue

        seen.add(value)
        values.append(value)

    return values


def _is_noise(
    value: str,
) -> bool:
    """
    Return whether a value is LinkedIn rendering noise.
    """
    return value in _NOISE or value.startswith(
        (
            "$L",
            "com.linkedin.sdui.",
            "ProfileNullStateCardAnchor",
            "profile_",
        )
    )


def get_collection(
    data: str,
    identifiers: str | tuple[str, ...],
) -> tuple[str, dict[str, str]] | None:
    """
    Find and resolve a collection matching any of `identifiers`.

    `identifiers` accepts more than one candidate substring so callers can
    match either the stable `collectionId`-style prefix (e.g.
    "profile_EducationTopLevelSection_") or the older component-key style
    ("EducationTopLevelSection") without having to guess which one a given
    response uses.

    A collection's own definition embeds `"collectionId":"<identifier>..."`
    literally, so that exact anchor is tried first for every candidate.
    Only if none match does this fall back to a loose substring search
    over every definition - the loose search alone is unsafe, because the
    profile-root node's value typically *mentions* every sibling section's
    name too (as part of a componentKey reference), and being first in
    stream order it wins a plain substring search before the actual,
    much smaller, collection definition is ever reached.
    """

    if isinstance(identifiers, str):
        identifiers = (identifiers,)

    definitions = extract_definitions(data)

    for identifier in identifiers:
        marker = f'"collectionId":"{identifier}'

        collection_key = next(
            (key for key, value in definitions.items() if marker in value),
            None,
        )

        if collection_key is not None:
            return (
                resolve_refs(definitions[collection_key], definitions),
                definitions,
            )

    collection_key = next(
        (
            key
            for key, value in definitions.items()
            if any(identifier.lower() in value.lower() for identifier in identifiers)
        ),
        None,
    )

    if collection_key is None:
        return None

    return (
        resolve_refs(
            definitions[collection_key],
            definitions,
        ),
        definitions,
    )


def get_collection_items(
    collection: str,
    definitions: dict[str, str],
) -> list[str]:
    """
    Split a collection into resolved entity items.
    """

    matches = list(
        re.finditer(
            r'"key":"entity-collection-item-[^"]+"',
            collection,
        )
    )

    items: list[str] = []

    for index, match in enumerate(matches):
        start = match.start()

        end = (
            matches[index + 1].start() if index + 1 < len(matches) else len(collection)
        )

        items.append(
            resolve_refs(
                collection[start:end],
                definitions,
            )
        )

    return items


def extract_target_url(
    data: str,
) -> str | None:
    """
    Return the first outbound URL an item's click action navigates to.

    LinkedIn wraps most external links (e.g. credential verification links)
    in a `/safety/go/?url=...` redirect - this decodes that wrapper back to
    the real destination. Links that aren't wrapped (e.g. project media
    links) are returned as-is.
    """

    match = _TARGET_URL_RE.search(data)

    if match is None:
        return None

    url = match.group(1)
    parsed = urlparse(url)

    if parsed.netloc.endswith("linkedin.com") and parsed.path.startswith("/safety/go"):
        target = parse_qs(parsed.query).get("url")

        if target:
            return unquote(target[0])

    return url
