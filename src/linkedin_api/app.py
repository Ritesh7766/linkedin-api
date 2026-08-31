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


@app.post("/profile")
def profile(request: ProfileRequest) -> ProfileResponse:
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
    return ProfileResponse(
        profile=profile,
        experience=experience,
    )
