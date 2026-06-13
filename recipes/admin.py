from django.contrib import admin

from .models import Category, Ingredient, Recipe, RecipeStep


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1
    fields = ("position", "section", "amount", "unit", "name", "note")
    ordering = ("position",)


class RecipeStepInline(admin.StackedInline):
    model = RecipeStep
    extra = 1
    fields = ("position", "instruction")
    ordering = ("position",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "base_servings", "category_list")
    search_fields = ("title", "ingredients__name")
    filter_horizontal = ("categories",)
    inlines = (IngredientInline, RecipeStepInline)
    readonly_fields = ("slug",)
    fieldsets = (
        (None, {"fields": ("title", "slug", "image", "base_servings", "categories")}),
        (
            "Image attribution",
            {
                "fields": ("image_credit", "image_credit_url"),
                "description": "Complete these fields when the image licence requires credit.",
            },
        ),
        (
            "Recipe source",
            {
                "fields": ("source_name", "source_url"),
                "description": "Optional link to the original recipe or inspiration.",
            },
        ),
    )

    @admin.display(description="Categories")
    def category_list(self, recipe):
        return ", ".join(recipe.categories.values_list("name", flat=True))


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    readonly_fields = ("slug",)
