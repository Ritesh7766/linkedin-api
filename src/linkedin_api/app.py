from fastapi import FastAPI

from linkedin_api.client import LinkedInClient
from linkedin_api.models import ProfileRequest, ProfileResponse
from linkedin_api.parsers.education import get_education
from linkedin_api.parsers.experience import get_experience
from linkedin_api.parsers.profile import get_profile


app = FastAPI(
    title="LinkedIn API",
    version="0.1.0",
)


@app.post("/profile")
def profile(
    request: ProfileRequest,
) -> ProfileResponse:
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
    education = get_education(
        client,
        request.vanity_name,
        profile_data.profile_id,
    )
    return ProfileResponse(
        profile=profile_data,
        experience=experience,
        education=education,
    )
