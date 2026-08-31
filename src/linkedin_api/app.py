from fastapi import FastAPI

from linkedin_api.client import LinkedInClient
from linkedin_api.models import ProfileRequest, ProfileResponse
from linkedin_api.parsers.experience import get_experience
from linkedin_api.parsers.profile import get_profile
from linkedin_api.parsers.section import get_parsed_sections
from linkedin_api.parsers.skills import get_skills

app = FastAPI(
    title="LinkedIn API",
    version="0.1.0",
)


@app.post("/profile")
def profile(
    request: ProfileRequest,
) -> ProfileResponse:
    """
    Fetch and assemble a LinkedIn profile.

    Parameters
    ----------
    request : ProfileRequest
        Vanity name of the LinkedIn profile to fetch.

    Returns
    -------
    ProfileResponse
        Assembled profile, including experience, education, skills,
        certifications, and projects.
    """
    client = LinkedInClient()
    profile_data = get_profile(
        client,
        request.vanity_name,
    )
    experience = get_experience(
        client,
        request.vanity_name,
    )
    skills = get_skills(
        client,
        request.vanity_name,
    )
    sections = get_parsed_sections(
        client,
        request.vanity_name,
        profile_data.profile_id,
    )
    return ProfileResponse(
        profile=profile_data,
        experience=experience,
        education=sections["education"],
        skills=skills,
        certifications=sections["certifications"],
        projects=sections["projects"],
    )
