from pydantic import BaseModel


class ComponentResponse(BaseModel):
    """
    Response returned by a LinkedIn component request.

    Parameters
    ----------
    component : str
        Identifier of the LinkedIn component that was requested.
    status_code : int
        HTTP status code returned by LinkedIn.
    data : str
        Raw response body returned by the component endpoint.
    """

    component: str
    status_code: int
    data: str


class Experience(BaseModel):
    """
    LinkedIn work experience entry.

    Parameters
    ----------
    company : str or None
        Company name.
    title : str or None
        Job title.
    employment_type : str or None
        Employment type.
    dates : str or None
        Employment dates.
    location : str or None
        Job location.
    company_duration : str or None
        Total duration at the company.
    """

    company: str | None
    title: str | None
    employment_type: str | None = None
    dates: str | None
    location: str | None = None
    company_duration: str | None = None


class Profile(BaseModel):
    """
    LinkedIn profile data.

    Parameters
    ----------
    profile_id : str or None
        LinkedIn profile ID.
    member_id : str or None
        LinkedIn member ID.
    followers : int or None
        Number of profile followers.
    activity_url : str or None
        URL to the profile's recent activity.
    about : str or None
        Profile About section.
    """

    profile_id: str | None = None
    member_id: str | None = None
    followers: int | None = None
    activity_url: str | None = None
    about: str | None = None


class Education(BaseModel):
    """
    LinkedIn education entry.

    Parameters
    ----------
    school : str or None
        Name of the educational institution.
    degree : str or None
        Degree obtained.
    field_of_study : str or None
        Field or subject of study.
    dates : str or None
        Education date range.
    grade : str or None
        Reported grade (e.g. "CGPA - 9.5 (upto 1st term)").
    description : str or None
        Free text under the entry - relevant coursework, activities, etc.
    """

    school: str | None
    degree: str | None = None
    field_of_study: str | None = None
    dates: str | None = None
    grade: str | None = None
    description: str | None = None


class Skill(BaseModel):
    """
    LinkedIn skill.

    Parameters
    ----------
    name : str
        Skill name.
    """

    name: str


class Certification(BaseModel):
    """
    LinkedIn license or certification entry.

    Parameters
    ----------
    name : str
        Certification/license title.
    issuing_organization : str or None
        Organization that issued it.
    issue_date : str or None
        Issue date as displayed (e.g. "Sep 2025").
    credential_id : str or None
        Credential ID, if shown.
    credential_url : str or None
        Verification URL, decoded from LinkedIn's redirect wrapper if
        present.
    """

    name: str
    issuing_organization: str | None = None
    issue_date: str | None = None
    credential_id: str | None = None
    credential_url: str | None = None


class Project(BaseModel):
    """
    LinkedIn project entry.

    Parameters
    ----------
    name : str
        Project title.
    description : str or None
        Project description text.
    url : str or None
        Linked project URL (e.g. a GitHub repo), if present.
    """

    name: str
    description: str | None = None
    url: str | None = None


class ProfileRequest(BaseModel):
    """
    Profile identifier required to fetch a profile.

    Parameters
    ----------
    vanity_name : str
        Vanity name of the LinkedIn profile to fetch.
    """

    vanity_name: str


class ProfileResponse(BaseModel):
    """
    Complete LinkedIn profile response.

    Parameters
    ----------
    profile : Profile
        Top-level profile data.
    experience : list of Experience
        Work experience entries.
    education : list of Education
        Education entries.
    skills : list of Skill
        Skill entries.
    certifications : list of Certification
        License/certification entries.
    projects : list of Project
        Project entries.
    """

    profile: Profile
    experience: list[Experience]
    education: list[Education]
    skills: list[Skill]
    certifications: list[Certification]
    projects: list[Project]
