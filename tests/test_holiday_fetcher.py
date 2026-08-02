import unittest

from holiday_fetcher import extract_holidays


class HolidayFetcherTests(unittest.TestCase):
    def test_extract_holidays_flattens_govuk_payload(self):
        payload = {
            "england-and-wales": {
                "events": [
                    {"title": "New Year's Day", "date": "2027-01-01"},
                    {"title": "Good Friday", "date": "2027-04-14"},
                ]
            },
            "scotland": {
                "events": [
                    {"title": "Early May Bank Holiday", "date": "2027-05-03"},
                ]
            },
        }

        holidays = extract_holidays(payload)

        self.assertEqual(len(holidays), 3)
        self.assertEqual(holidays[0]["date"], "2027-01-01")
        self.assertEqual(holidays[0]["name"], "New Year's Day")
        self.assertEqual(holidays[-1]["name"], "Early May Bank Holiday")


if __name__ == "__main__":
    unittest.main()
