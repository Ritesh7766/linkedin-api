from linkedin_api.client import LinkedInClient


EXPERIENCE_COMPONENT = (
    "com.linkedin.sdui.generated.profile.dsl.impl." "profileCardsExperienceOnly"
)


def fetch_experience(
    client: LinkedInClient,
    vanity_name: str,
    profile_id: str,
) -> str:
    """
    Fetch the Experience component for a LinkedIn profile.

    Parameters
    ----------
    client : LinkedInClient
        Authenticated LinkedIn client used to make the request.
    vanity_name : str
        Vanity name of the LinkedIn profile.
    profile_id : str
        LinkedIn profile ID required by the Experience component.

    Returns
    -------
    str
        Raw response body returned by LinkedIn.
    """
    payload = {
        "clientArguments": {
            "payload": {
                "isSelfView": False,
                "vanityName": vanity_name,
                "replaceableSectionArgs": {
                    "vanityName": vanity_name,
                    "hideCardsForGoldenGate": False,
                    "shouldSetupReplaceableComponent": True,
                    "vieweeProfileId": profile_id,
                    "isSelfView": False,
                    "isSelfViewResolved": False,
                },
            },
            "states": [],
            "requestMetadata": {"$type": "proto.sdui.common.RequestMetadata"},
            "screenId": "com.linkedin.sdui.flagshipnav.profile.Profile",
            "knownTemplateIds": [],
        }
    }

    return client.fetch_component(
        component=EXPERIENCE_COMPONENT,
        payload=payload,
    )
