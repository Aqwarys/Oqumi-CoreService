from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class Category(models.Model):
    """
    Model representing a course category.
    """

    code = models.CharField(
        max_length=10,
        primary_key=True,
        unique=True,
        db_index=True,
        help_text="Unique category code, always stored in uppercase.",
    )
    name = models.CharField(
        max_length=256, unique=True, db_index=True, help_text="Category name."
    )
    description = models.CharField(
        max_length=512, null=True, blank=True, help_text="Category description."
    )
    image = models.ImageField(
        upload_to="categories/", null=True, blank=True, help_text="Category image."
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure code is always uppercase
        self.code = self.code.upper()
        super().save(*args, **kwargs)


class Course(models.Model):
    """
    Model representing a course.
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        help_text="Category this course belongs to.",
    )
    name = models.CharField(
        max_length=256, unique=True, db_index=True, help_text="Course name."
    )
    slug = models.SlugField(
        unique=True, help_text="URL-friendly slug generated from name."
    )
    description = models.CharField(
        max_length=512, null=True, blank=True, help_text="Course description."
    )
    image = models.ImageField(
        upload_to="courses/", null=True, blank=True, help_text="Course image."
    )
    is_free = models.BooleanField(default=True, help_text="Whether the course is free.")
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Course cost if not free.",
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_free"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        # Validation: If not free, cost must be provided
        if not self.is_free and self.cost is None:
            raise ValidationError("Cost must be provided for non-free courses.")
        super().clean()

    def save(self, *args, **kwargs):
        # Generate slug from name if not set
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()  # Run validation
        super().save(*args, **kwargs)
