from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch

import requests
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Experience, Intro, Project


class HomepageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Intro.objects.create(
            description="Portfolio introduction",
            image="portfolio/images/profile.jpg",
            image_small="portfolio/images/profile-small.jpg",
        )
        Experience.objects.create(
            title="Example Company",
            subtitle="Developer",
            skills="Python, Django",
            start_date=2024,
            description="Built useful things.",
        )
        Project.objects.create(
            title="First project",
            description="An example project.",
            image="portfolio/images/project-one.jpg",
            skill1="Python",
            skill2="Django",
        )
        Project.objects.create(
            title="Second project",
            description="Another example project.",
            image="portfolio/images/project-two.jpg",
            skill1="Python",
            skill2="JavaScript",
        )

    def test_intro_links_cooking_to_recipes_without_nav_tab(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'And I love <a href="{reverse("recipes:list")}">cooking</a>!',
            html=True,
        )
        self.assertNotContains(response, ">Recipes</a>")

    def test_homepage_loads_database_content_and_common_skills(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portfolio introduction")
        self.assertContains(response, "First project")
        self.assertContains(response, "Example Company")
        self.assertEqual(
            response.context["most_common_skills"],
            ["Python", "Django", "JavaScript"],
        )

    def test_project_static_assets_are_discoverable(self):
        self.assertIsNotNone(finders.find("portfolio/css/home.css"))
        self.assertIsNotNone(finders.find("portfolio/js/on-reload.js"))
        self.assertIsNotNone(finders.find("recipes/css/recipes.css"))


@override_settings(
    SPOTIFY_CLIENT_ID="client-id",
    SPOTIFY_CLIENT_SECRET="client-secret",
    SPOTIFY_REFRESH_TOKEN="refresh-token",
)
class SpotifyApiTests(TestCase):
    @patch("portfolio.views.requests.post")
    @patch("portfolio.views.requests.get")
    def test_now_playing_returns_current_track(self, mock_get, mock_post):
        token_response = Mock()
        token_response.json.return_value = {"access_token": "token"}
        token_response.raise_for_status.return_value = None
        mock_post.return_value = token_response

        current_response = Mock(status_code=200)
        current_response.json.return_value = {
            "is_playing": True,
            "item": {
                "name": "Test Song",
                "artists": [{"name": "Test Artist"}],
                "album": {"images": [{"url": "https://example.com/cover.jpg"}]},
                "external_urls": {"spotify": "https://example.com/song"},
            },
        }
        mock_get.return_value = current_response

        response = self.client.get(reverse("now-playing"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "isPlaying": True,
                "title": "Test Song",
                "artist": "Test Artist",
                "albumImageUrl": "https://example.com/cover.jpg",
                "songUrl": "https://example.com/song",
            },
        )

    @patch(
        "portfolio.views.get_access_token",
        side_effect=requests.exceptions.ConnectionError,
    )
    def test_now_playing_handles_spotify_failure(self, _mock_token):
        with redirect_stdout(StringIO()):
            response = self.client.get(reverse("now-playing"))

        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
            response.content,
            {"error": "Could not connect to Spotify."},
        )
