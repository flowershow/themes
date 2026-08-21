#!/usr/bin/env python3
"""Smoke-check every standard route on a published theme demo."""

import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


STANDARD_ROUTES = (
    ("/", None),
    ("/docs/kitchen-sink", "Kitchen Sink"),
    ("/blog", "Blog"),
    ("/blog/first-post", "The First Post"),
)


def fetch(url: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": "flowershow-themes-verifier/1"})
    try:
        with urlopen(request, timeout=20) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as error:
        return error.code, ""
    except (URLError, TimeoutError):
        return 0, ""


def verify(base_url: str, homepage_marker: str, compatibility_url: str = "") -> int:
    failed = False
    for route, route_marker in STANDARD_ROUTES:
        url = urljoin(base_url.rstrip("/") + "/", route.lstrip("/"))
        separator = "&" if "?" in url else "?"
        status, body = fetch(f"{url}{separator}verify=routes")
        expected = homepage_marker if route == "/" else route_marker
        if status == 200 and expected and expected.casefold() in body.casefold():
            print(f"  PASS  standard demo route {route} responds with {expected}")
        else:
            print(
                f"  FAIL  standard demo route {route} failed "
                f"(HTTP {status}; expected {expected})"
            )
            failed = True

    if compatibility_url:
        separator = "&" if "?" in compatibility_url else "?"
        status, body = fetch(f"{compatibility_url}{separator}verify=compatibility")
        if status == 200 and homepage_marker.casefold() in body.casefold():
            print("  PASS  landing compatibility route serves the showcase")
        else:
            print(
                "  FAIL  landing compatibility route failed "
                f"(HTTP {status}; expected {homepage_marker})"
            )
            failed = True
    return int(failed)


def main(argv: list[str]) -> int:
    if len(argv) not in {3, 4}:
        print(
            "usage: verify-demo-routes.py BASE_URL HOMEPAGE_MARKER [COMPATIBILITY_URL]",
            file=sys.stderr,
        )
        return 2
    return verify(argv[1], argv[2], argv[3] if len(argv) == 4 else "")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
