from linkedin_api.client.client import LinkedInClient
from linkedin_api.utils import build_detail_payload

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
    payload = build_detail_payload(
        screen_id=EXPERIENCE_SCREEN_ID,
        page_key=EXPERIENCE_PAGE_KEY,
        vanity_name=vanity_name,
    )

    return client.fetch_detail(
        vanity_name=vanity_name,
        detail="experience",
        payload=payload,
    )
