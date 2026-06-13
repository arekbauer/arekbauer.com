from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Recipe(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    image = models.ImageField(upload_to="recipes/images/")
    image_credit = models.CharField(
        max_length=150,
        blank=True,
        help_text="For example: Sous Chef / CC BY 2.0",
    )
    image_credit_url = models.URLField(
        blank=True,
        help_text="Link to the image source or licence page.",
    )
    source_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional label for the original recipe source.",
    )
    source_url = models.URLField(
        blank=True,
        help_text="Link to the original recipe, video, or inspiration.",
    )
    base_servings = models.PositiveSmallIntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        help_text="The serving count used for the ingredient quantities below.",
    )
    categories = models.ManyToManyField(Category, related_name="recipes", blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.title)
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.001"))],
        help_text="Leave blank for entries such as salt to taste.",
    )
    unit = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=150)
    note = models.CharField(max_length=150, blank=True)
    section = models.CharField(
        max_length=60,
        blank=True,
        help_text="Optional heading such as Toppings or Bibimbap sauce.",
    )
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.name


class RecipeStep(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="steps"
    )
    instruction = models.TextField()
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.recipe}: step {self.position}"


def _unique_slug(instance, value):
    slug_root = slugify(value) or instance.__class__.__name__.lower()
    slug = slug_root
    suffix = 2
    queryset = instance.__class__.objects.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.filter(slug=slug).exists():
        slug = f"{slug_root}-{suffix}"
        suffix += 1
    return slug
