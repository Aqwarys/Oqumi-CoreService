from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quiz
from .permissions import IsAdminUserOnly
from .serializers import (
    QuizCheckResultSerializer,
    QuizCheckSerializer,
    QuizDetailSerializer,
    QuizEditSerializer,
    QuizSerializer,
)
from .services import check_quiz_answers, update_quiz_with_questions


class QuizAccessMixin:
    queryset = Quiz.objects.prefetch_related("questions").all()

    def get_quiz(self, quiz_id: int) -> Quiz:
        return get_object_or_404(self.queryset, id=quiz_id)

    def ensure_pass_access(self, request, quiz: Quiz) -> None:
        if quiz.is_free:
            return
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")
        if not hasattr(request.user, "subscription") or not request.user.subscription.is_active:
            raise PermissionDenied("Active subscription required to access this quiz.")


@extend_schema(
    tags=["Quizzes"],
    summary="Create quiz",
    description="Creates a new quiz. Only admin users can create quizzes.",
    request=QuizSerializer,
    responses={
        201: OpenApiResponse(
            response=QuizSerializer,
            description="Quiz created successfully.",
            examples=[
                OpenApiExample(
                    "Quiz Creation",
                    value={
                        "id": 1,
                        "course": 1,
                        "lesson": None,
                        "title": "Python Basics Quiz",
                        "description": "Final quiz for Python basics module.",
                        "is_free": False,
                        "cost": "9.99",
                        "image": None,
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Bad Request"),
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden"),
    },
)
class QuizCreateView(APIView):
    permission_classes = [IsAdminUserOnly]

    def post(self, request):
        serializer = QuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save()
        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Quizzes"],
    summary="Get quiz for passing",
    description=(
        "Returns quiz data for passing. If quiz is paid, authentication and active "
        "subscription are required. Response excludes `correct` and `explanation` fields."
    ),
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Quiz ID",
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=QuizDetailSerializer,
            description="Quiz details for passing.",
            examples=[
                OpenApiExample(
                    "Quiz Passing",
                    value={
                        "id": 1,
                        "course": 1,
                        "lesson": None,
                        "title": "Python Basics Quiz",
                        "description": "Answer questions to complete module.",
                        "is_free": True,
                        "cost": None,
                        "image": None,
                        "questions": [
                            {
                                "id": 10,
                                "type": "single",
                                "content": {"type": "doc", "content": []},
                                "image": None,
                                "options": ["A", "B", "C"],
                                "score": 1,
                            }
                        ],
                    },
                )
            ],
        ),
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Not Found"),
    },
)
class QuizDetailView(QuizAccessMixin, APIView):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUserOnly()]
        return super().get_permissions()

    def get(self, request, id):
        quiz = self.get_quiz(id)
        self.ensure_pass_access(request, quiz)
        return Response(QuizDetailSerializer(quiz).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Quizzes"],
        summary="Delete quiz",
        description="Deletes a quiz and all its questions. Only admin users can delete quizzes.",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Quiz ID",
                required=True,
            )
        ],
        responses={
            204: OpenApiResponse(description="Quiz deleted successfully."),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not Found"),
        },
    )
    def delete(self, request, id):
        quiz = self.get_quiz(id)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["Quizzes"],
    summary="Get quiz for editing",
    description=(
        "Returns complete quiz payload for editing by admin users, including "
        "question `correct` answers and `explanation`."
    ),
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Quiz ID",
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(response=QuizEditSerializer, description="Editable quiz payload."),
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Not Found"),
    },
)
class QuizEditView(QuizAccessMixin, APIView):
    permission_classes = [IsAdminUserOnly]

    def get(self, request, id):
        quiz = self.get_quiz(id)
        return Response(QuizEditSerializer(quiz).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Quizzes"],
    summary="Full update quiz with questions",
    description=(
        "Updates quiz fields and synchronizes nested questions in one transaction:\n"
        "- Updates existing questions by `id`\n"
        "- Creates new questions without `id`\n"
        "- Deletes removed questions"
    ),
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Quiz ID",
            required=True,
        )
    ],
    request=QuizEditSerializer,
    responses={
        200: OpenApiResponse(
            response=QuizEditSerializer,
            description="Quiz and questions updated successfully.",
            examples=[
                OpenApiExample(
                    "Quiz Full Update",
                    value={
                        "id": 1,
                        "course": 1,
                        "lesson": None,
                        "title": "Python Basics Quiz (Updated)",
                        "description": "Updated quiz content.",
                        "is_free": False,
                        "cost": "7.99",
                        "image": None,
                        "questions": [
                            {
                                "id": 1,
                                "type": "single",
                                "content": {"type": "doc", "content": []},
                                "image": None,
                                "options": ["A", "B", "C"],
                                "correct": [1],
                                "score": 2,
                                "explanation": "B is correct because ...",
                            },
                            {
                                "type": "multiple",
                                "content": {"type": "doc", "content": []},
                                "image": None,
                                "options": ["X", "Y", "Z"],
                                "correct": [0, 2],
                                "score": 3,
                                "explanation": "X and Z are correct.",
                            },
                        ],
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Bad Request"),
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Not Found"),
    },
)
class QuizFullUpdateView(QuizAccessMixin, APIView):
    permission_classes = [IsAdminUserOnly]

    def put(self, request, id):
        quiz = self.get_quiz(id)
        serializer = QuizEditSerializer(instance=quiz, data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = update_quiz_with_questions(quiz=quiz, validated_data=serializer.validated_data)
        return Response(QuizEditSerializer(quiz).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Quizzes"],
    summary="Check quiz answers",
    description=(
        "Checks submitted answers and returns per-question grading details. "
        "Public for free quizzes, otherwise requires authentication and active subscription."
    ),
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Quiz ID",
            required=True,
        )
    ],
    request=QuizCheckSerializer,
    responses={
        200: OpenApiResponse(
            response=QuizCheckResultSerializer(many=True),
            description="Per-question grading result.",
            examples=[
                OpenApiExample(
                    "Quiz Check",
                    value=[
                        {
                            "question_id": 42,
                            "is_correct": True,
                            "score": 1,
                            "explanation": "Option B is the correct one.",
                            "correct_answer": [1],
                        }
                    ],
                )
            ],
        ),
        400: OpenApiResponse(description="Bad Request"),
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Not Found"),
    },
)
class QuizCheckView(QuizAccessMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request, id):
        quiz = self.get_quiz(id)
        self.ensure_pass_access(request, quiz)

        serializer = QuizCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = check_quiz_answers(quiz=quiz, answers=serializer.validated_data["answers"])
        return Response(result, status=status.HTTP_200_OK)
