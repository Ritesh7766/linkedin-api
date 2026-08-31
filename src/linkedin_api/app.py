from fastapi import FastAPI

from linkedin_api.client import LinkedInClient
from linkedin_api.models import ProfileRequest, ProfileResponse
from linkedin_api.parsers.experience import get_experience
from linkedin_api.parsers.profile import get_profile
from linkedin_api.parsers.section import get_parsed_sections


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
    education, skills = get_parsed_sections(
        client,
        request.vanity_name,
        profile_data.profile_id,
    )
    print(education, skills)
    return ProfileResponse(
        profile=profile_data,
        experience=experience,
        education=education,
        skills=skills,
    )
