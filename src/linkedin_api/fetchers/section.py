from linkedin_api.client import LinkedInClient


def fetch_profile_section(
    client: LinkedInClient,
    vanity_name: str,
    profile_id: str,
    part: int,
) -> str:
    """
    Fetch a LinkedIn profile section part.

    Parameters
    ----------
    client : LinkedInClient
        Authenticated LinkedIn client used to make the request.

    vanity_name : str
        Vanity name of the LinkedIn profile.

    profile_id : str
        LinkedIn profile ID.

    part : int
        Profile section part identifier.

    Returns
    -------
    str
        Raw response body returned by LinkedIn.
    """

    component = (
        "com.linkedin.sdui.generated.profile.dsl.impl."
        f"profileCardsBelowActivityPart{part}"
    )

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
            "requestMetadata": {
                "$type": "proto.sdui.common.RequestMetadata",
            },
            "screenId": ("com.linkedin.sdui.flagshipnav.profile.Profile"),
            "knownTemplateIds": [],
        }
    }

    return client.fetch_component(
        component=component,
        payload=payload,
    )
