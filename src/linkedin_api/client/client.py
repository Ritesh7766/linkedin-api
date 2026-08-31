from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar

import requests

from linkedin_api.client.config import settings


@dataclass(frozen=True)
class LinkedInClient:
    """
    Client for making authenticated requests to LinkedIn's component API.

    Authentication credentials are loaded from environment variables.

    Parameters
    ----------
    timeout : float, default=30.0
        Maximum number of seconds to wait for an HTTP response.

    Environment Variables
    ---------------------
    LINKEDIN_LI_AT : str
        LinkedIn session authentication cookie value.

    LINKEDIN_JSESSIONID : str
        LinkedIn session ID and CSRF token value.

    Attributes
    ----------
    BASE_URL : str
        Base URL for LinkedIn.

    COMPONENT_ENDPOINT : str
        Endpoint used to request LinkedIn components.
    """

    timeout: float = 30.0

    BASE_URL: ClassVar[str] = "https://www.linkedin.com"

    COMPONENT_ENDPOINT: ClassVar[str] = (
        f"{BASE_URL}/flagship-web/rsc-action/actions/component"
    )

    @cached_property
    def session(self) -> requests.Session:
        """
        Return the configured HTTP session.

        Returns
        -------
        requests.Session
            Session configured with the required headers and
            LinkedIn authentication cookies.
        """

        session = requests.Session()

        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/152.0.0.0 Safari/537.36"
                ),
                "Accept": "*/*",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Content-Type": "application/json",
                "csrf-token": settings.linkedin_jsessionid,
                "x-restli-protocol-version": "2.0.0",
                "x-li-rsc-stream": "true",
            }
        )

        session.cookies.update(
            {
                "li_at": settings.linkedin_li_at,
                "JSESSIONID": f'"{settings.linkedin_jsessionid}"',
            }
        )

        return session

    def fetch_component(
        self,
        *,
        component: str,
        payload: dict,
    ) -> str:
        """
        Fetch a LinkedIn component.

        Parameters
        ----------
        component : str
            Identifier of the LinkedIn component to request.

        payload : dict
            JSON request body expected by the component endpoint.

        Returns
        -------
        str
            Raw response body returned by LinkedIn.

        Raises
        ------
        requests.HTTPError
            If LinkedIn returns an unsuccessful HTTP status code.

        requests.RequestException
            If the request fails due to a network or transport error.
        """

        response = self.session.post(
            self.COMPONENT_ENDPOINT,
            params={
                "componentId": component,
                "sduiid": component,
            },
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.text
