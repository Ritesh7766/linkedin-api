from linkedin_api.client.client import LinkedInClient
from linkedin_api.utils import build_detail_payload


SKILLS_SCREEN_ID = "com.linkedin.sdui.flagshipnav.profile." "ProfileSkillDetails"

SKILLS_PAGE_KEY = "profile_view_base_skills_details"


def fetch_skills(
    client: LinkedInClient,
    vanity_name: str,
) -> str:
    """
    Fetch the raw Skills details response for a LinkedIn profile.

    Parameters
    ----------
    client : LinkedInClient
        Authenticated LinkedIn client used to make the request.

    vanity_name : str
        Vanity name of the LinkedIn profile.

    Returns
    -------
    str
        Raw RSC response returned by LinkedIn's Skills details
        endpoint.
    """
    payload = build_detail_payload(
        screen_id=SKILLS_SCREEN_ID,
        page_key=SKILLS_PAGE_KEY,
        vanity_name=vanity_name,
    )

    return client.fetch_detail(
        vanity_name=vanity_name,
        detail="skills",
        payload=payload,
    )
