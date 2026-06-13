from django.test import TestCase
from django.urls import reverse


class HomepageTests(TestCase):
    def test_intro_links_cooking_to_recipes_without_nav_tab(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'And I love <a href="{reverse("recipes:list")}">cooking</a>!',
            html=True,
        )
        self.assertNotContains(response, ">Recipes</a>")
