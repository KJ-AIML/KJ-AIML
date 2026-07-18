from __future__ import annotations

import argparse
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from contributions import parse_contribution_html, write_data


URL = "https://github.com/users/KJ-AIML/contributions"


def fetch(url: str = URL, attempts: int = 3) -> str:
    request = Request(url, headers={"User-Agent": "KJ-AIML-profile-art/1.0 (+https://github.com/KJ-AIML)"})
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=20) as response:
                if response.status != 200:
                    raise RuntimeError(f"GitHub returned HTTP {response.status}")
                return response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, RuntimeError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"Unable to fetch contribution calendar after {attempts} attempts: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and normalize KJ-AIML's public GitHub contribution calendar.")
    parser.add_argument("--output", type=Path, default=Path("data/contributions.json"))
    args = parser.parse_args()
    records, period = parse_contribution_html(fetch())
    write_data(args.output, records, period)
    print(f"Wrote {len(records)} contribution days to {args.output}")


if __name__ == "__main__":
    main()
