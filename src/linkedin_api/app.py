from fastapi import FastAPI
from pydantic import BaseModel

from linkedin_api.client import LinkedInClient
from linkedin_api.models import Profile
from linkedin_api.parsers.profile_parsers import get_profile

app = FastAPI(
    title="LinkedIn API",
    version="0.1.0",
)


class ProfileRequest(BaseModel):
    """
    Credentials and profile identifier required to fetch a profile.

    Parameters
    ----------
    csrf_token : str
        LinkedIn JSESSIONID value used as the CSRF token.
    auth_token : str
        LinkedIn li_at authentication cookie value.
    vanity_name : str
        Vanity name of the LinkedIn profile to fetch.
    """

    csrf_token: str
    auth_token: str
    vanity_name: str


@app.post("/profile", response_model=Profile)
def profile(request: ProfileRequest) -> Profile:
    """
    Fetch a LinkedIn profile.

    Parameters
    ----------
    request : ProfileRequest
        LinkedIn session credentials and profile vanity name.

    Returns
    -------
    Profile
        Parsed LinkedIn profile data.
    """

    client = LinkedInClient(
        li_at=request.auth_token,
        jsessionid=request.csrf_token,
    )

    return get_profile(
        client,
        request.vanity_name,
    )
