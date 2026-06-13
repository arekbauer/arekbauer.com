from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase
from django.urls import reverse

from .services import VLRService


def match_item(
    *,
    tournament="VCT 2026: Masters London",
    utc="2026-06-13T12:00:00Z",
    status="UPCOMING",
    ago="",
):
    return {
        "tournament": tournament,
        "utc": utc,
        "status": status,
        "ago": ago,
        "timestamp": 1781352000,
        "event": "Upper Final",
        "teams": [
            {"name": "Team Alpha", "score": 2},
            {"name": "Team Beta", "score": 1},
        ],
    }


class VLRServiceTests(SimpleTestCase):
    def setUp(self):
        self.now = datetime(2026, 6, 13, 12, 0, tzinfo=ZoneInfo("Europe/London"))

    def test_process_matches_buckets_live_today_and_tomorrow(self):
        raw_matches = [
            match_item(status="LIVE"),
            match_item(status="UPCOMING"),
            match_item(utc="2026-06-14T12:00:00Z"),
            match_item(tournament="Unrelated tournament"),
        ]

        result = VLRService._process_matches(raw_matches, self.now)

        self.assertEqual(len(result["live"]), 1)
        self.assertEqual(len(result["t_up"]), 1)
        self.assertEqual(len(result["tom_up"]), 1)
        self.assertEqual(result["live"][0]["tournament"], "Masters London")

    def test_process_results_buckets_today_and_yesterday(self):
        raw_results = [
            match_item(ago="2h"),
            match_item(ago="1d"),
            match_item(ago="3d"),
        ]

        result = VLRService._process_results(raw_results, self.now)

        self.assertEqual(len(result["t_res"]), 1)
        self.assertEqual(len(result["y_res"]), 1)

    @patch("trmnl_service.services.requests.get")
    def test_fetch_data_returns_empty_list_on_network_failure(self, mock_get):
        mock_get.side_effect = RuntimeError("network unavailable")

        self.assertEqual(VLRService._fetch_data("https://example.com"), [])


class VCTTickerViewTests(SimpleTestCase):
    @patch("trmnl_service.views.VLRService.get_vct_dashboard_data")
    def test_ticker_returns_dashboard_data(self, mock_dashboard):
        mock_dashboard.return_value = {
            "live": [],
            "t_up": [],
            "tom_up": [],
            "y_res": [],
            "t_res": [],
            "last_updated": "12:00",
        }

        response = self.client.get(reverse("trmnl_vct_ticker"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, mock_dashboard.return_value)

    @patch("trmnl_service.views.VLRService.get_vct_dashboard_data")
    def test_ticker_returns_bad_gateway_for_service_error(self, mock_dashboard):
        mock_dashboard.return_value = {"error": "upstream unavailable"}

        response = self.client.get(reverse("trmnl_vct_ticker"))

        self.assertEqual(response.status_code, 502)
