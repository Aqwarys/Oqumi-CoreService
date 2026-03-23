from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Course


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin for Category model.
    """

    list_display = ["code", "name", "description", "image_preview"]
    search_fields = ["code", "name"]
    ordering = ["name"]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No image"

    image_preview.short_description = "Image Preview"

    def clean_code(self):
        """Ensure code is uppercase."""
        if hasattr(self, "code"):
            self.code = self.code.upper()


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Admin for Course model.
    """

    list_display = ["name", "category", "is_free", "cost", "image_preview"]
    list_filter = ["is_free", "category"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No image"

    image_preview.short_description = "Image Preview"
