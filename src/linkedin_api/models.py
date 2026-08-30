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


class Profile(BaseModel):
    """
    Parsed data from a LinkedIn Above Activity response.

    Parameters
    ----------
    profile_id : str or None
        LinkedIn profile ID extracted from the response.
    about : str or None
        About text extracted from the response.
    """

    profile_id: str | None
    about: str | None