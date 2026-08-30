import re

from linkedin_api.models import Profile


def _parse_above_activity(data: str) -> dict[str, str | None]:
    """
    Parse profile ID and About text from a raw LinkedIn
    Above Activity response.

    Parameters
    ----------
    data : str
        Raw response returned by the LinkedIn Above Activity component.

    Returns
    -------
    AboveActivity
        Parsed profile ID and About text.
    """
    profile_id_match = re.search(
        r"ref(ACo[A-Za-z0-9_-]+)About",
        data,
    )
    about_match = re.search(
        r'"textProps":\{'
        r'"fontFamily":"sans",'
        r'"fontSize":"small",'
        r".*?"
        r'"lineClamp":\d+',
        data,
        re.DOTALL,
    )
    about = (
        "\n\n".join(
            re.findall(
                r'"children":\[(?:null,\s*)?"((?:\\.|[^"\\])*)"',
                about_match.group(0),
            )
        )
        if about_match
        else None
    )
    return {
        "profile_id": (profile_id_match.group(1) if profile_id_match else None),
        "about": about or None,
    }


def _parse_activity(data: str) -> dict[str, str | int | bool | None]:
    """
    Parse profile activity information from an Activity response.

    Parameters
    ----------
    data : str
        Raw response returned by the LinkedIn Activity component.

    Returns
    -------
    dict[str, str | int | bool | None]
        Extracted activity information.
    """
    member_match = re.search(
        r"urn:li:member:(\d+)",
        data,
    )

    member_id = member_match.group(1) if member_match else None

    followers_match = re.search(
        r'"children":\["([\d,]+) followers"\]',
        data,
    )

    activity_match = re.search(
        r"https://www\.linkedin\.com/in/" r"[^/]+/recent-activity/all/",
        data,
    )

    return {
        "member_id": member_id,
        "followers": (
            int(followers_match.group(1).replace(",", "")) if followers_match else None
        ),
        "activity_url": (activity_match.group(0) if activity_match else None),
    }


def get_profile(
    raw_above_activity: str,
    raw_activity: str,
) -> Profile:
    """
    Fetch and assemble LinkedIn profile data.

    Parameters
    ----------
    client : LinkedInClient
        Authenticated LinkedIn client.
    vanity_name : str
        Vanity name of the LinkedIn profile.

    Returns
    -------
    Profile
        Combined profile data parsed from the available components.
    """

    above_activity = _parse_above_activity(raw_above_activity)

    activity = _parse_activity(raw_activity)

    return Profile(
        **above_activity,
        **activity,
    )
