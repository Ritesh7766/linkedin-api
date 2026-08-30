# fetchers/profile.py

from linkedin_api.client import LinkedInClient


ABOVE_ACTIVITY_COMPONENT = (
    "com.linkedin.sdui.generated.profile.dsl.impl."
    "profileCardsAboveActivity"
)


def fetch_above_activity(
    client: LinkedInClient,
    vanity_name: str,
) -> str:
    payload = {
        "clientArguments": {
            "payload": {
                "isSelfView": False,
                "vanityName": vanity_name,
                "replaceableSectionArgs": {
                    "vanityName": vanity_name,
                    "hideCardsForGoldenGate": False,
                    "shouldSetupReplaceableComponent": True,
                    "isSelfView": False,
                    "isSelfViewResolved": False,
                },
            },
            "states": [],
            "requestMetadata": {
                "$type": "proto.sdui.common.RequestMetadata"
            },
            "screenId": (
                "com.linkedin.sdui.flagshipnav.profile.Profile"
            ),
            "knownTemplateIds": [],
        }
    }

    return client.fetch_component(
        component=ABOVE_ACTIVITY_COMPONENT,
        payload=payload,
    )