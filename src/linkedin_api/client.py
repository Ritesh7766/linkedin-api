from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar

import requests


@dataclass(frozen=True)
class LinkedInClient:
    li_at: str
    jsessionid: str
    timeout: float = 30.0

    BASE_URL: ClassVar[str] = "https://www.linkedin.com"
    COMPONENT_ENDPOINT: ClassVar[str] = (
        f"{BASE_URL}/flagship-web/"
        "rsc-action/actions/component"
    )

    @cached_property
    def session(self) -> requests.Session:
        session = requests.Session()

        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/152.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Content-Type": "application/json",
            "csrf-token": self.jsessionid,
            "x-restli-protocol-version": "2.0.0",
            "x-li-rsc-stream": "true",
        })

        session.cookies.update({
            "li_at": self.li_at,
            "JSESSIONID": f'"{self.jsessionid}"',
        })

        return session

    def fetch_component(
        self,
        *,
        component: str,
        payload: dict,
    ) -> str:
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
