from django.urls import path
from .views import CategoryListView, CourseDetailView

app_name = "courses"

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("<slug:slug>/", CourseDetailView.as_view(), name="course-detail"),
]
