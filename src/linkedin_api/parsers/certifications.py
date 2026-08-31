from linkedin_api.models import Certification
from linkedin_api.parsers.common import (
    extract_target_url,
    extract_text,
    get_collection,
    get_collection_items,
)

_CERTIFICATIONS_COLLECTION = (
    "profile_CertificationTopLevel_",
    "CertificationTopLevel",
)

_NOISE_PREFIXES = ("Show all", "Show credential")


def _is_noise(value: str) -> bool:
    return value.startswith(_NOISE_PREFIXES)


def _parse_item(item: str) -> Certification | None:
    values = [value for value in extract_text(item) if not _is_noise(value)]

    values = [
        value
        for index, value in enumerate(values)
        if index == 0 or value != values[index - 1]
    ]

    if not values:
        return None

    name = values[0]
    issuing_organization: str | None = None
    issue_date: str | None = None
    credential_id: str | None = None

    for value in values[1:]:
        if value.startswith("Issued "):
            issue_date = value.removeprefix("Issued ").strip()
        elif value.startswith("Credential ID "):
            credential_id = value.removeprefix("Credential ID ").strip()
        elif issuing_organization is None:
            issuing_organization = value

    return Certification(
        name=name,
        issuing_organization=issuing_organization,
        issue_date=issue_date,
        credential_id=credential_id,
        credential_url=extract_target_url(item),
    )


def parse_certifications(data: str) -> list[Certification]:
    """
    Parse licenses/certifications from one raw LinkedIn profile section
    response.
    """

    result = get_collection(data, _CERTIFICATIONS_COLLECTION)

    if result is None:
        return []

    collection, definitions = result
    certifications: list[Certification] = []

    for item in get_collection_items(collection, definitions):
        parsed = _parse_item(item)

        if parsed is not None:
            certifications.append(parsed)

    return certifications
