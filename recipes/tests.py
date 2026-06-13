from decimal import Decimal

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from .admin import IngredientInline, RecipeStepInline
from .models import Category, Ingredient, Recipe, RecipeStep


class RecipeModelTests(TestCase):
    def test_recipe_and_category_generate_unique_slugs(self):
        first_recipe = Recipe.objects.create(
            title="Tomato Pasta", image="recipes/test.gif", base_servings=4
        )
        second_recipe = Recipe.objects.create(
            title="Tomato Pasta", image="recipes/test.gif", base_servings=2
        )
        first_category = Category.objects.create(name="Quick Meals")

        self.assertEqual(first_recipe.slug, "tomato-pasta")
        self.assertEqual(second_recipe.slug, "tomato-pasta-2")
        self.assertEqual(first_category.slug, "quick-meals")

    def test_recipe_supports_image_attribution(self):
        recipe = Recipe.objects.create(
            title="Rice Bowl",
            image="recipes/test.gif",
            image_credit="Example Photographer / CC BY 2.0",
            image_credit_url="https://example.com/photo",
        )

        self.assertEqual(recipe.image_credit, "Example Photographer / CC BY 2.0")

    def test_recipe_supports_an_optional_source(self):
        recipe = Recipe.objects.create(
            title="Inspired Rice Bowl",
            image="recipes/test.gif",
            source_name="Original video",
            source_url="https://example.com/video",
        )

        self.assertEqual(recipe.source_name, "Original video")

    def test_related_items_are_ordered_by_position_then_id(self):
        recipe = Recipe.objects.create(
            title="Soup", image="recipes/test.gif", base_servings=4
        )
        later = Ingredient.objects.create(
            recipe=recipe, amount=1, unit="tsp", name="Salt", position=2
        )
        first = Ingredient.objects.create(
            recipe=recipe, amount=2, unit="cups", name="Stock", position=1
        )
        second_step = RecipeStep.objects.create(
            recipe=recipe, instruction="Serve.", position=2
        )
        first_step = RecipeStep.objects.create(
            recipe=recipe, instruction="Simmer.", position=1
        )

        self.assertEqual(list(recipe.ingredients.all()), [first, later])
        self.assertEqual(list(recipe.steps.all()), [first_step, second_step])

    def test_ingredient_amount_may_be_blank_but_not_zero(self):
        recipe = Recipe.objects.create(
            title="Seasoning", image="recipes/test.gif", base_servings=1
        )
        optional_amount = Ingredient(
            recipe=recipe, amount=None, name="Salt", note="to taste"
        )
        optional_amount.full_clean()

        invalid_amount = Ingredient(
            recipe=recipe, amount=Decimal("0"), name="Pepper"
        )
        with self.assertRaises(ValidationError):
            invalid_amount.full_clean()


@override_settings(SECURE_SSL_REDIRECT=False)
class RecipeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dinner = Category.objects.create(name="Dinner")
        cls.quick = Category.objects.create(name="Quick")
        cls.recipe = Recipe.objects.create(
            title="Lemon Pasta",
            image="recipes/test.gif",
            base_servings=4,
            source_name="Original video",
            source_url="https://example.com/video",
        )
        cls.recipe.categories.add(cls.dinner, cls.quick)
        Ingredient.objects.create(
            recipe=cls.recipe,
            amount=Decimal("1.500"),
            unit="cups",
            name="Pasta",
            section="Main",
            position=1,
        )
        Ingredient.objects.create(
            recipe=cls.recipe,
            amount=None,
            name="Black pepper",
            note="to taste",
            position=2,
        )
        RecipeStep.objects.create(
            recipe=cls.recipe, instruction="Cook the pasta.", position=1
        )
        cls.other_recipe = Recipe.objects.create(
            title="Apple Cake", image="recipes/test.gif", base_servings=8
        )

    def test_recipe_list_displays_all_recipes_and_categories(self):
        response = self.client.get(reverse("recipes:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)
        self.assertContains(response, self.other_recipe.title)
        self.assertContains(response, self.dinner.name)
        self.assertContains(response, 'loading="lazy"')

    def test_recipe_list_filters_by_category(self):
        response = self.client.get(
            reverse("recipes:list"), {"category": self.dinner.slug}
        )

        self.assertContains(response, self.recipe.title)
        self.assertNotContains(response, self.other_recipe.title)
        self.assertEqual(response.context["selected_category"], self.dinner)

    def test_unknown_category_returns_404(self):
        response = self.client.get(
            reverse("recipes:list"), {"category": "not-a-category"}
        )

        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_exposes_scaling_data_and_unscaled_entries(self):
        response = self.client.get(
            reverse("recipes:detail", kwargs={"slug": self.recipe.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-base-servings="4"')
        self.assertContains(response, 'data-base-amount="1.500"')
        self.assertContains(response, "Black pepper")
        self.assertContains(response, "Cook the pasta.")
        self.assertContains(response, "Main")
        self.assertContains(response, "Original video")
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener noreferrer"')

    def test_unknown_recipe_returns_404(self):
        response = self.client.get(
            reverse("recipes:detail", kwargs={"slug": "missing"})
        )

        self.assertEqual(response.status_code, 404)


class RecipeAdminTests(TestCase):
    def test_recipe_admin_uses_ingredient_and_step_inlines(self):
        recipe_admin = admin.site._registry[Recipe]
        inline_models = [inline.model for inline in recipe_admin.inlines]

        self.assertEqual(
            inline_models,
            [IngredientInline.model, RecipeStepInline.model],
        )
        self.assertIn(Category, admin.site._registry)
