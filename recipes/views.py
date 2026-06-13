from django.shortcuts import get_object_or_404, render

from .models import Category, Recipe


def recipe_list(request):
    recipes = Recipe.objects.prefetch_related("categories")
    categories = Category.objects.all()
    selected_category = None

    category_slug = request.GET.get("category")
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        recipes = recipes.filter(categories=selected_category)

    return render(
        request,
        "recipes/recipe_list.html",
        {
            "recipes": recipes,
            "categories": categories,
            "selected_category": selected_category,
        },
    )


def recipe_detail(request, slug):
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related("categories", "ingredients", "steps"),
        slug=slug,
    )
    return render(request, "recipes/recipe_detail.html", {"recipe": recipe})
