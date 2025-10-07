
from rest_framework import serializers
from .models import (
    Syllabus,
    PreviousPaper,
    Keyword,
    InterviewQuestion,
    MockTest,
    Question,
    TestAttempt,
    UserAnswer,
    Formula,
    DailyQuiz,
)

from django.db import models


class SyllabusSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Syllabus
        fields = ['id', 'board', 'class_level', 'subject', 'content', 'pdf_url']

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.pdf and request:
            return request.build_absolute_uri(obj.pdf.url)
        elif obj.pdf:
            return obj.pdf.url
        return None


class PreviousPaperSerializer(serializers.ModelSerializer):
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = PreviousPaper
        fields = ['title', 'year', 'exam_type', 'pdf_url']

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        elif obj.file:
            return obj.file.url
        return None


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['subject', 'title', 'word', 'meaning']


class InterviewQuestionSerializer(serializers.ModelSerializer):
    department_label = serializers.CharField(source='get_department_display', read_only=True)

    class Meta:
        model = InterviewQuestion
        fields = ['id', 'department', 'department_label', 'question', 'answer']


class DailyQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyQuiz
        fields = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'options']

    def get_options(self, obj):
        return {
            'A': obj.option_a,
            'B': obj.option_b,
            'C': obj.option_c,
            'D': obj.option_d,
        }


class MockTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockTest
        fields = ['id', 'subject', 'description', 'date']


class UserAnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(source='question', queryset=Question.objects.all())

    class Meta:
        model = UserAnswer
        fields = ['question_id', 'selected_option']


class TestAttemptSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    mock_test = MockTestSerializer()
    test_name = serializers.CharField(source='mock_test.subject', read_only=True)
    taken_on = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    answers = UserAnswerSerializer(many=True)

    class Meta:
        model = TestAttempt
        fields = ['id', 'user', 'mock_test', 'test_name', 'score', 'taken_on', 'answers']
        read_only_fields = ['score', 'taken_on', 'user']


class AttemptedQuestionDetailSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    option_a = serializers.CharField(source='question.option_a', read_only=True)
    option_b = serializers.CharField(source='question.option_b', read_only=True)
    option_c = serializers.CharField(source='question.option_c', read_only=True)
    option_d = serializers.CharField(source='question.option_d', read_only=True)
    correct_option = serializers.CharField(source='question.correct_option', read_only=True)
    user_answer = serializers.CharField(source='selected_option', read_only=True)

    class Meta:
        model = UserAnswer
        fields = [
            'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_option', 'user_answer'
        ]


class AttemptDetailSerializer(serializers.ModelSerializer):
    questions = AttemptedQuestionDetailSerializer(source='answers', many=True)
    total_questions = serializers.SerializerMethodField()
    attended_count = serializers.SerializerMethodField()
    correct_count = serializers.SerializerMethodField()
    incorrect_count = serializers.SerializerMethodField()

    class Meta:
        model = TestAttempt
        fields = [
            'id', 'mock_test', 'score', 'taken_on',
            'total_questions', 'attended_count', 'correct_count', 'incorrect_count', 'questions'
        ]

    def get_total_questions(self, obj):
        return obj.mock_test.questions.count()

    def get_attended_count(self, obj):
        return obj.answers.count()

    def get_correct_count(self, obj):
        return obj.answers.filter(selected_option=models.F('question__correct_option')).count()

    def get_incorrect_count(self, obj):
        return obj.answers.exclude(selected_option=models.F('question__correct_option')).count()


class FormulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formula
        fields = ['id', 'subject', 'heading', 'formula']
