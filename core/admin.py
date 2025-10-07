
import csv
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.auth import get_user_model
from django.utils.timezone import localdate

from .models import (
    Syllabus, MockTest, Question, TestAttempt, UserAnswer,
    PreviousPaper, Result, Keyword, DailyQuiz,
    InterviewQuestion, Formula, DailyQuizAttempt
)

User = get_user_model()


@admin.register(PreviousPaper)
class PreviousPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'exam_type')
    list_filter = ('year', 'exam_type')


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('subject', 'title', 'word', 'short_meaning')
    list_filter = ('subject', 'title')
    search_fields = ('word', 'title')

    def short_meaning(self, obj):
        return (obj.meaning[:70] + '...') if len(obj.meaning) > 70 else obj.meaning
    short_meaning.short_description = 'Meaning'


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ('department', 'short_question', 'short_answer')
    list_filter = ('department',)
    search_fields = ('question', 'answer')

    def short_question(self, obj):
        return (obj.question[:60] + '...') if len(obj.question) > 60 else obj.question
    short_question.short_description = "Question"

    def short_answer(self, obj):
        return (obj.answer[:60] + '...') if len(obj.answer) > 60 else obj.answer
    short_answer.short_description = "Answer"


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(MockTest)
class MockTestAdmin(admin.ModelAdmin):
    list_display = ('subject', 'date')
    inlines = [QuestionInline]
    search_fields = ('subject',)
    fields = ('subject', 'class_level', 'description', 'date')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:mocktest_id>/upload-csv/', self.admin_site.admin_view(self.upload_csv), name='mocktest_upload_csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request, mocktest_id):
        mock_test = MockTest.objects.get(pk=mocktest_id)
        if request.method == "POST":
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                self.message_user(request, "No file uploaded.", level=messages.ERROR)
                return redirect(request.path)

            if not csv_file.name.endswith('.csv'):
                self.message_user(request, "Uploaded file is not CSV.", level=messages.ERROR)
                return redirect(request.path)

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            success_count = 0
            errors = []

            for i, row in enumerate(reader, start=1):
                question_text = row.get("question")
                option_a = row.get("option1")
                option_b = row.get("option2")
                option_c = row.get("option3")
                option_d = row.get("option4")
                answer = row.get("answer")

                if answer:
                    answer = answer.strip().upper()

                if not all([question_text, option_a, option_b, option_c, option_d, answer]):
                    errors.append(f"Row {i}: Missing fields.")
                    continue

                option_map = {'A': option_a, 'B': option_b, 'C': option_c, 'D': option_d}
                if answer not in option_map:
                    errors.append(f"Row {i}: Answer must be one of A, B, C, D.")
                    continue

                Question.objects.create(
                    mock_test=mock_test,
                    question_text=question_text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_option=answer,
                )
                success_count += 1

            if success_count:
                self.message_user(request, f"{success_count} questions uploaded successfully.")
            if errors:
                self.message_user(request, f"Errors: {'; '.join(errors)}", level=messages.ERROR)

            return redirect(f"/admin/{self.model._meta.app_label}/{self.model._meta.model_name}/{mocktest_id}/change/")

        context = dict(
            self.admin_site.each_context(request),
            mock_test=mock_test,
        )
        return render(request, "admin/upload_csv.html", context)


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ('question', 'selected_option')
    can_delete = False


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'mock_test', 'score', 'taken_on')
    list_filter = ('taken_on', 'mock_test')
    search_fields = ('user__username', 'mock_test__subject')
    readonly_fields = ('user', 'mock_test', 'score', 'taken_on')
    inlines = [UserAnswerInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    pass


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    pass


@admin.register(DailyQuiz)
class DailyQuizAdmin(admin.ModelAdmin):
    list_display = ('short_question', 'quiz_date', 'correct_option', 'is_today')
    list_filter = ('quiz_date',)
    search_fields = ('question',)
    ordering = ('-quiz_date',)
    date_hierarchy = 'quiz_date'

    def short_question(self, obj):
        return (obj.question[:50] + '...') if len(obj.question) > 50 else obj.question
    short_question.short_description = 'Question'

    def is_today(self, obj):
        return obj.quiz_date == localdate()
    is_today.boolean = True
    is_today.short_description = "Today's Quiz"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-daily-quiz/', self.admin_site.admin_view(self.upload_daily_quiz), name='dailyquiz_upload'),
        ]
        return custom_urls + urls

    def upload_daily_quiz(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get('csv_file')
            quiz_date = request.POST.get('quiz_date')

            if not csv_file:
                self.message_user(request, "No file uploaded.", level=messages.ERROR)
                return redirect(request.path)

            if not quiz_date:
                self.message_user(request, "Please select a quiz date.", level=messages.ERROR)
                return redirect(request.path)

            if not csv_file.name.endswith('.csv'):
                self.message_user(request, "Uploaded file is not CSV.", level=messages.ERROR)
                return redirect(request.path)

            # Clear existing questions for this date
            DailyQuiz.objects.filter(quiz_date=quiz_date).delete()

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            success_count = 0
            errors = []

            for i, row in enumerate(reader, start=1):
                question_text = row.get("question")
                option_a = row.get("option1")
                option_b = row.get("option2")
                option_c = row.get("option3")
                option_d = row.get("option4")
                answer = row.get("answer")

                if answer:
                    answer = answer.strip().upper()

                if not all([question_text, option_a, option_b, option_c, option_d, answer]):
                    errors.append(f"Row {i}: Missing fields.")
                    continue

                option_map = {'A': option_a, 'B': option_b, 'C': option_c, 'D': option_d}
                if answer not in option_map:
                    errors.append(f"Row {i}: Answer must be one of A, B, C, D.")
                    continue

                DailyQuiz.objects.create(
                    question=question_text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_option=answer,
                    quiz_date=quiz_date,
                )
                success_count += 1

            if success_count:
                self.message_user(request, f"{success_count} daily quiz questions uploaded for {quiz_date}.")
            if errors:
                self.message_user(request, f"Errors: {'; '.join(errors)}", level=messages.ERROR)

            return redirect(f"/admin/{self.model._meta.app_label}/{self.model._meta.model_name}/")

        context = dict(
            self.admin_site.each_context(request),
            today=localdate(),
        )
        return render(request, "admin/upload_daily_quiz.html", context)


@admin.register(Formula)
class FormulaAdmin(admin.ModelAdmin):
    list_display = ('subject', 'heading', 'short_formula')
    search_fields = ('subject', 'heading', 'formula')
    list_filter = ('subject',)

    def short_formula(self, obj):
        return (obj.formula[:60] + '...') if len(obj.formula) > 60 else obj.formula
    short_formula.short_description = "Formula"


@admin.register(DailyQuizAttempt)
class DailyQuizAttemptAdmin(admin.ModelAdmin):
    ordering = ['quiz_date']
    readonly_fields = ['score', 'percent', 'quiz_date', 'total_questions']
    list_display = ['user', 'score', 'percent', 'quiz_date', 'total_questions']
    list_filter = ['quiz_date']
    search_fields = ('user__username',)

    def total_questions(self, obj):
        return DailyQuiz.objects.filter(quiz_date=obj.quiz_date).count()
    total_questions.short_description = 'Total Questions'
