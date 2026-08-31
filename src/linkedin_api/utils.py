def build_detail_payload(
    *,
    screen_id: str,
    page_key: str,
    vanity_name: str,
) -> dict:
    """Build the SDUI payload used by LinkedIn profile detail screens."""
    return {
        "$type": "proto.sdui.actions.core.NavigateToScreen",
        "screenId": screen_id,
        "pageKey": page_key,
        "requestedArguments": {
            "payload": {
                "vanityName": vanity_name,
            },
            "states": [],
            "requestMetadata": {
                "$type": "proto.sdui.common.RequestMetadata",
            },
            "screenId": "",
            "knownTemplateIds": [],
        },
    }
