import time
import requests

from typing import Any, Iterator

from urllib.parse import urljoin


class BentleyApiError(RuntimeError):
    """Custom exception for Bentley API errors."""
    pass

API_BASE_URL = "https://api.bentley.com"

BENTLEY_ACCEPT = (
    "application/vnd.bentley.itwin-platform.v1+json"
)

BENTLEY_HEADERS = {
    "Accept": "application/vnd.bentley.itwin-platform.v1+json"
}

def iter_bentley_pages(
    initial_url: str,
    access_token: str,
    *,
    accept: str = "application/vnd.bentley.itwin-platform.v1+json",
    timeout_seconds: int = 60,
    max_retries: int = 5,
) -> Iterator[dict[str, Any]]:

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {access_token}",
        "Accept": accept,
    })

    next_url: str | None = initial_url
    seen_urls: set[str] = set()

    while next_url:
        if next_url in seen_urls:
            raise BentleyApiError(
                "The API returned a next-page URL that has already been used."
            )

        seen_urls.add(next_url)

        for attempt in range(max_retries):
            response = session.get(next_url, timeout=timeout_seconds)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                delay = int(retry_after) if retry_after else 2 ** attempt
                time.sleep(delay)
                continue

            if 500 <= response.status_code < 600:
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            break
        else:
            raise BentleyApiError(
                f"Request failed after {max_retries} attempts: {next_url}"
            )

        payload = response.json()
        yield payload

        href = (
            payload.get("_links", {})
                   .get("next", {})
                   .get("href")
        )

        next_url = urljoin(next_url, href) if href else None
