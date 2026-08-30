import re

from linkedin_api.models import Profile


def parse_above_activity(data: str) -> Profile:
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
    return Profile(
        profile_id=(profile_id_match.group(1) if profile_id_match else None),
        about=about or None,
    )
