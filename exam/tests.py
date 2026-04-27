from __future__ import annotations

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .models import Module, Problem, Subject
from .services import build_exam


class ExamBuildTests(TestCase):
    def _create_subject(self, *, name: str, max_score: int) -> Subject:
        return Subject.objects.create(
            name=name,
            slug=name.lower().replace(" ", "-"),
            description=None,
            type=Subject.SubjectType.MANDATORY,
            duration_sec=3600,
            max_score=max_score,
        )

    def _create_module(self, subject: Subject, title: str) -> Module:
        return Module.objects.create(subject=subject, title=title)

    def _create_problem(self, module: Module, index: int) -> Problem:
        return Problem.objects.create(
            module=module,
            content={"text": f"Question {index}"},
            type=Problem.ProblemType.SINGLE,
            options=["A", "B", "C"],
            correct=[0],
            explanation="Because A is correct.",
        )

    def _create_problems(self, module: Module, count: int) -> None:
        for index in range(count):
            self._create_problem(module, index)

    def _get_module_counts(self, problem_ids: list[int]) -> dict[int, int]:
        counts: dict[int, int] = {}
        for problem in Problem.objects.filter(id__in=problem_ids).only(
            "id", "module_id"
        ):
            counts[problem.module_id] = counts.get(problem.module_id, 0) + 1
        return counts

    def test_build_exam_even_distribution_when_possible(self):
        subject = self._create_subject(name="Math", max_score=4)
        module_a = self._create_module(subject, "Algebra")
        module_b = self._create_module(subject, "Geometry")
        self._create_problems(module_a, 5)
        self._create_problems(module_b, 5)

        payload = build_exam(subject)
        problem_ids = [problem["id"] for problem in payload["subjects"][0]["problems"]]
        counts = self._get_module_counts(problem_ids)

        self.assertEqual(payload["total_problem_count"], 4)
        self.assertEqual(counts[module_a.id], 2)
        self.assertEqual(counts[module_b.id], 2)

    def test_build_exam_falls_back_to_capacity_distribution(self):
        subject = self._create_subject(name="Physics", max_score=50)
        module_a = self._create_module(subject, "Mechanics")
        module_b = self._create_module(subject, "Optics")
        self._create_problems(module_a, 20)
        self._create_problems(module_b, 30)

        payload = build_exam(subject)
        problem_ids = [problem["id"] for problem in payload["subjects"][0]["problems"]]
        counts = self._get_module_counts(problem_ids)

        self.assertEqual(payload["total_problem_count"], 50)
        self.assertEqual(counts[module_a.id], 20)
        self.assertEqual(counts[module_b.id], 30)

    def test_build_exam_raises_when_insufficient_total_capacity(self):
        subject = self._create_subject(name="Chemistry", max_score=6)
        module_a = self._create_module(subject, "Organic")
        module_b = self._create_module(subject, "Inorganic")
        self._create_problems(module_a, 2)
        self._create_problems(module_b, 3)

        with self.assertRaises(ValidationError):
            build_exam(subject)

    def test_build_exam_raises_when_module_has_no_problems(self):
        subject = self._create_subject(name="Biology", max_score=5)
        module_a = self._create_module(subject, "Cells")
        module_b = self._create_module(subject, "Genetics")
        self._create_problems(module_b, 5)

        with self.assertRaises(ValidationError):
            build_exam(subject)
