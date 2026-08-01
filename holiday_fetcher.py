import argparse
import json
import sys
import urllib.error
import urllib.request

API_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
COUNTRY_CODE = "GB"


def get_holidays(year: int):
    """Fetch public holidays for the UK from the Nager.Date API."""
    url = API_URL.format(year=year, country_code=COUNTRY_CODE)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            body = response.read()
            return json.loads(body.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP error {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def format_holidays(holidays):
    """Format the API holiday data into user-friendly strings."""
    lines = []
    for holiday in holidays:
        date = holiday.get("date")
        name = holiday.get("localName") or holiday.get("name")
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
