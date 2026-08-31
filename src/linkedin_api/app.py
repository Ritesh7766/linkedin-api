from fastapi import FastAPI

from linkedin_api.client.client import LinkedInClient
from linkedin_api.models.models import ProfileRequest, ProfileResponse
from linkedin_api.parsers.experience import get_experience
from linkedin_api.parsers.profile import (
    get_profile,
)

app = FastAPI(
    title="LinkedIn API",
    version="0.1.0",
)


@app.post(
    "/profile",
    response_model=ProfileResponse,
)
def get_linkedin_profile(
    request: ProfileRequest,
) -> ProfileResponse:
    """
    Fetch a LinkedIn profile and its work experience.
    """

    client = LinkedInClient()
    profile_data = get_profile(
        client,
        request.vanity_name,
    )
    experience = get_experience(
        client,
        request.vanity_name,
        profile_data.profile_id,
    )
    return ProfileResponse(
        profile=profile_data,
        experience=experience,
    )
