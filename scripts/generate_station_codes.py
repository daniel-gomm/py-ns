#!/usr/bin/env python3
"""Generate py_ns/station_codes.py from the live NS Stations API (v3).

Usage:
    uv run scripts/generate_station_codes.py

The script reads NS_API_KEY from a .env file (or the environment) in the
project root and writes py_ns/station_codes.py.  Commit the result.
"""

import os
import re
import unicodedata
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT = PROJECT_ROOT / "py_ns" / "station_codes.py"
STATIONS_URL = "https://gateway.apiportal.ns.nl/nsapp-stations/v3"


def _load_api_key() -> str:
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("NS_API_KEY="):
                return line.split("=", 1)[1].strip()
    key = os.environ.get("NS_API_KEY", "")
    if not key:
        raise SystemExit("NS_API_KEY not found in .env or environment.")
    return key


def _to_identifier(name: str) -> str:
    """Convert a station long name to a valid snake_case Python identifier."""
    # Strip diacritics (é → e, ü → u, etc.)
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", errors="ignore").decode()
    # Drop apostrophes and dots; map separators to underscores
    name = name.replace("'", "").replace(".", "")
    name = re.sub(r"[\s/\-]+", "_", name)
    # Replace any remaining non-alphanumeric chars with underscore
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = name.lower()
    # Collapse consecutive underscores and strip leading/trailing
    name = re.sub(r"_+", "_", name).strip("_")
    # Python identifiers cannot start with a digit
    if name and name[0].isdigit():
        name = f"_{name}"
    return name or "_unknown"


def _fetch_stations(api_key: str) -> list[dict]:
    with httpx.Client(headers={"Ocp-Apim-Subscription-Key": api_key}) as client:
        response = client.get(STATIONS_URL)
        response.raise_for_status()
    return response.json()["payload"]


def _build_members(stations: list[dict]) -> list[tuple[str, str, str]]:
    """Return (identifier, code, comment) triples, deduplicated."""
    # Count how many stations map to the same base identifier
    from collections import Counter
    base_ids = Counter(_to_identifier(s["names"]["long"]) for s in stations)

    members = []
    for s in sorted(stations, key=lambda x: x["names"]["long"]):
        code = s["id"]["code"]
        long_name = s["names"]["long"]
        country = s["country"]
        base = _to_identifier(long_name)
        # Disambiguate colliding names by appending the station code
        ident = f"{base}_{code.lower()}" if base_ids[base] > 1 else base
        comment = f"{long_name} ({country})"
        members.append((ident, code, comment))

    return members


def _render(members: list[tuple[str, str, str]]) -> str:
    lines = [
        "# Auto-generated — do not edit manually.",
        "# To regenerate: uv run scripts/generate_station_codes.py",
        "",
        "from enum import StrEnum",
        "",
        "",
        "class StationCode(StrEnum):",
        '    """NS station codes for all stations served by NS international trains.',
        "",
        "    Each member's value is the short station code accepted by all NS API",
        "    endpoints (e.g. ``StationCode.amsterdam_centraal == 'ASD'``).",
        '    """',
        "",
    ]
    for ident, code, comment in members:
        lines.append(f'    {ident} = "{code}"  # {comment}')
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    api_key = _load_api_key()
    print("Fetching stations from NS API…")
    stations = _fetch_stations(api_key)
    print(f"  {len(stations)} stations received.")

    members = _build_members(stations)
    OUTPUT.write_text(_render(members))
    print(f"Written {len(members)} entries to {OUTPUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
