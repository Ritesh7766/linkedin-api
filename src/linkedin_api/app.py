from fastapi import FastAPI
from pydantic import BaseModel

from linkedin_api.client.client import LinkedInClient
from linkedin_api.parsers.experience import get_experience
from linkedin_api.parsers.profile import (
    get_profile,
)

app = FastAPI(
    title="LinkedIn API",
    version="0.1.0",
)


class ProfileRequest(BaseModel):
    """
    Credentials and profile identifier required to fetch a profile.

    Parameters
    ----------
    vanity_name : str
        Vanity name of the LinkedIn profile to fetch.
    """

    vanity_name: str


@app.post("/profile")
def profile(request: ProfileRequest) -> dict:
    client = LinkedInClient()

    profile = get_profile(
        client,
        request.vanity_name,
    )

    experience = get_experience(
        client,
        request.vanity_name,
        profile.profile_id,
    )

    return {
        "profile": profile,
        "experience": experience,
    }
