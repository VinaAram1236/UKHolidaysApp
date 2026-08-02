import argparse
import json
import sys
import urllib.error
import urllib.request

API_URL = "https://www.gov.uk/bank-holidays.json"
REGION_ALIASES = {
    "england": "england-and-wales",
    "wales": "england-and-wales",
    "england-and-wales": "england-and-wales",
    "scotland": "scotland",
    "northern-ireland": "northern-ireland",
    "ni": "northern-ireland",
}


def get_holidays(year: int, region=None):
    """Fetch UK bank holidays from the GOV.UK API."""
    try:
        with urllib.request.urlopen(API_URL, timeout=10) as response:
            body = response.read()
            payload = json.loads(body.decode("utf-8"))
            return extract_holidays(payload, year=year, region=region)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP error {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def extract_holidays(payload, year=None, region=None):
    """Flatten the GOV.UK bank holidays payload into a list of holiday records."""
    holidays = []
    seen = set()
    target_region = REGION_ALIASES.get((region or "").lower()) if region else None

    for key, division in payload.items():
        if target_region and key != target_region:
            continue
        for event in division.get("events", []):
            event_date = event.get("date")
            if not event_date:
                continue
            if year is not None and event_date[:4] != str(year):
                continue
            key_name = (event_date, event.get("title"))
            if key_name in seen:
                continue
            seen.add(key_name)
            holidays.append({"date": event_date, "name": event.get("title")})
    holidays.sort(key=lambda item: item["date"])
    return holidays


def format_holidays(holidays):
    """Format the holiday data into user-friendly strings."""
    lines = []
    for holiday in holidays:
        date = holiday.get("date")
        name = holiday.get("name")
        lines.append(f"{date} - {name}")
    return lines


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch UK public holidays for a given year using an external web API."
    )
    parser.add_argument(
        "year",
        type=int,
        help="The year to lookup public holidays for (for example, 2027).",
    )
    parser.add_argument(
        "--region",
        choices=["england", "wales", "england-and-wales", "scotland", "northern-ireland", "ni"],
        default=None,
        help="Optional region filter: england, wales, scotland, or northern-ireland.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    year = args.year

    if year < 1900 or year > 2100:
        print("Please provide a year between 1900 and 2100.")
        sys.exit(1)

    region = args.region
    print(f"Fetching UK public holidays for {year}{f' in {region}' if region else ''}...\n")

    try:
        holidays = get_holidays(year, region=region)
    except Exception as exc:
        print(f"Error fetching holidays: {exc}")
        sys.exit(1)

    if not holidays:
        print(f"No holidays returned for {year}.")
        return

    for line in format_holidays(holidays):
        print(line)


if __name__ == "__main__":
    main()
