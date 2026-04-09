from django.urls import path

from .views import (
    QuizCheckView,
    QuizCreateView,
    QuizDetailView,
    QuizEditView,
    QuizFullUpdateView,
)

urlpatterns = [
    path("", QuizCreateView.as_view(), name="quiz-create"),
    path("<int:id>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("<int:id>/edit/", QuizEditView.as_view(), name="quiz-edit"),
    path("<int:id>/full-update/", QuizFullUpdateView.as_view(), name="quiz-full-update"),
    path("<int:id>/check/", QuizCheckView.as_view(), name="quiz-check"),
]
