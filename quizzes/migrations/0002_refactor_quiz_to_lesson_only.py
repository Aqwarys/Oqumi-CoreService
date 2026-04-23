from django.db import migrations, models
import django.db.models.deletion


def assign_or_cleanup_orphan_quizzes(apps, _schema_editor):
    Quiz = apps.get_model("quizzes", "Quiz")
    Lesson = apps.get_model("lessons", "Lesson")

    orphan_quizzes = Quiz.objects.filter(lesson__isnull=True)
    if not orphan_quizzes.exists():
        return

    fallback_lesson = Lesson.objects.order_by("id").first()
    if fallback_lesson is not None:
        # Safe strategy (preferred): keep existing quizzes by attaching them to
        # the earliest lesson when lesson is missing (including old course-level quizzes).
        orphan_quizzes.update(lesson_id=fallback_lesson.id)
        return

    # No lessons exist, so attaching is impossible. Remove invalid quizzes to
    # prevent migration failure when lesson becomes non-nullable.
    orphan_quizzes.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            assign_or_cleanup_orphan_quizzes,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveConstraint(
            model_name="quiz",
            name="quiz_exactly_one_target",
        ),
        migrations.RemoveIndex(
            model_name="quiz",
            name="quizzes_qui_course__40d7d6_idx",
        ),
        migrations.AlterField(
            model_name="quiz",
            name="lesson",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="quizzes",
                to="lessons.lesson",
            ),
        ),
        migrations.RemoveField(
            model_name="quiz",
            name="course",
        ),
    ]
