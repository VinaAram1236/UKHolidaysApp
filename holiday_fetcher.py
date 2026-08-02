import argparse
import json
import sys
import urllib.error
import urllib.request

API_URL = "https://www.gov.uk/bank-holidays.json"


def get_holidays(year: int):
    """Fetch UK bank holidays from the GOV.UK API."""
    try:
        with urllib.request.urlopen(API_URL, timeout=10) as response:
            body = response.read()
            payload = json.loads(body.decode("utf-8"))
            return extract_holidays(payload, year=year)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP error {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def extract_holidays(payload, year=None):
    """Flatten the GOV.UK bank holidays payload into a list of holiday records."""
    holidays = []
    for division in payload.values():
        for event in division.get("events", []):
            event_date = event.get("date")
            if not event_date:
                continue
            if year is not None and event_date[:4] != str(year):
                continue
            holidays.append({"date": event_date, "name": event.get("title")})
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
    return parser.parse_args()


def main():
    args = parse_args()
    year = args.year

    if year < 1900 or year > 2100:
        print("Please provide a year between 1900 and 2100.")
        sys.exit(1)

    print(f"Fetching UK public holidays for {year}...\n")

    try:
        holidays = get_holidays(year)
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
