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
    company : str
        Company name.
    title : str
        Job title.
    employment_type : str or None
        Employment type.
    dates : str
        Employment dates.
    location : str or None
        Job location.
    company_duration : str or None
        Total duration at the company.
    company_id : str or None
        LinkedIn company ID.
    company_url : str or None
        LinkedIn company URL.
    """

    company: str | None
    title: str | None
    employment_type: str | None = None
    dates: str | None
    location: str | None = None
    company_duration: str | None = None
    company_id: str | None = None
    company_url: str | None = None


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


class ProfileResponse(BaseModel):
    """
    Complete LinkedIn profile response.
    """

    profile: Profile
    experience: list[Experience]
