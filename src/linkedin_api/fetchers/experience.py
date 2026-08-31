from linkedin_api.client.client import LinkedInClient

EXPERIENCE_SCREEN_ID = (
    "com.linkedin.sdui.flagshipnav.profile." "ProfileExperienceDetails"
)

EXPERIENCE_PAGE_KEY = "profile_view_base_position_details"


def fetch_experience(
    client: LinkedInClient,
    vanity_name: str,
) -> str:
    """
    Fetch the raw Experience details response for a LinkedIn profile.

    Parameters
    ----------
    client : LinkedInClient
        Authenticated LinkedIn client used to make the request.

    vanity_name : str
        Vanity name of the LinkedIn profile.

    Returns
    -------
    str
        Raw RSC response returned by LinkedIn's Experience details
        endpoint.
    """
    payload = {
        "$type": "proto.sdui.actions.core.NavigateToScreen",
        "screenId": EXPERIENCE_SCREEN_ID,
        "pageKey": EXPERIENCE_PAGE_KEY,
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

    return client.fetch_detail(
        vanity_name=vanity_name,
        detail="experience",
        payload=payload,
    )
