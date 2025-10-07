
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localdate, now
from django.http import JsonResponse, HttpResponseNotAllowed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, get_user_model
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from django.contrib.auth.password_validation import validate_password
from .models import (
    AIChatHistory, Syllabus, PreviousPaper, Keyword, InterviewQuestion,
    MockTest, Question, TestAttempt, UserAnswer,
    Formula, DailyQuiz, DailyQuizAttempt
)
from .serializers import (
    SyllabusSerializer, PreviousPaperSerializer, KeywordSerializer, InterviewQuestionSerializer,
    MockTestSerializer, QuestionSerializer, TestAttemptSerializer, UserAnswerSerializer,
    AttemptDetailSerializer, FormulaSerializer,
)

User = get_user_model()


# Read-Only API ViewSets

class SyllabusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Syllabus.objects.all()
    serializer_class = SyllabusSerializer


class PreviousPaperViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PreviousPaper.objects.all()
    serializer_class = PreviousPaperSerializer


class KeywordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer


class InterviewQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InterviewQuestion.objects.all()
    serializer_class = InterviewQuestionSerializer


class MockTestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MockTest.objects.all()
    serializer_class = MockTestSerializer


class FormulaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Formula.objects.all()
    serializer_class = FormulaSerializer


# Mock Test API Views

class QuestionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id):
        mock_test = get_object_or_404(MockTest, pk=test_id)
        questions = mock_test.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class SubmitTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id):
        user = request.user
        mock_test = get_object_or_404(MockTest, pk=test_id)
        answers = request.data.get('answers', {})

        questions = mock_test.questions.all()
        total_questions = questions.count()
        correct_count = 0

        attempt = TestAttempt.objects.create(user=user, mock_test=mock_test, score=0)

        for question in questions:
            selected_option = answers.get(str(question.id))
            if selected_option:
                UserAnswer.objects.create(attempt=attempt, question=question, selected_option=selected_option)
                if selected_option.upper() == question.correct_option.upper():
                    correct_count += 1

        score_percent = int((correct_count / total_questions) * 100) if total_questions else 0
        attempt.score = score_percent
        attempt.save()

        serializer = TestAttemptSerializer(attempt)
        return Response(serializer.data, status=201)


class TestAttemptListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attempts = TestAttempt.objects.filter(user=request.user).order_by('-taken_on')
        serializer = TestAttemptSerializer(attempts, many=True)
        return Response(serializer.data)


class TestAttemptDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):
        attempt = get_object_or_404(TestAttempt, pk=attempt_id, user=request.user)
        serializer = AttemptDetailSerializer(attempt)
        return Response(serializer.data)


# Daily Quiz API Views

class DailyQuizAttemptListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attempts = DailyQuizAttempt.objects.filter(user=request.user).order_by('-quiz_date')
        daily_quiz_list = [{
            'id': attempt.id,
            'score': attempt.score,
            'percent': attempt.percent,
            'date': attempt.quiz_date.strftime("%Y-%m-%d"),
        } for attempt in attempts]
        return Response(daily_quiz_list)


class DailyQuizAttemptDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):
        attempt = get_object_or_404(DailyQuizAttempt, pk=attempt_id, user=request.user)
        quiz_date = attempt.quiz_date
        questions = DailyQuiz.objects.filter(quiz_date=quiz_date).order_by('id')
        quiz_detail = []
        answers = attempt.answers if attempt.answers else []

        for idx, question in enumerate(questions):
            correct_option = (question.correct_option or '').upper()
            user_answer = answers[idx].upper() if idx < len(answers) and answers[idx] else ''
            quiz_detail.append({
                'question_text': question.question,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'correct_option': correct_option,
                'user_answer': user_answer,
                'is_correct': (correct_option == user_answer) if user_answer else False,
            })

        return Response({
            'total_questions': len(questions),
            'attended_count': len([a for a in answers if a]),
            'correct_count': attempt.score,
            'incorrect_count': len(questions) - attempt.score,
            'questions': quiz_detail,
            'score': attempt.score,
            'percent': attempt.percent,
            'date': quiz_date.strftime("%Y-%m-%d"),
        })


# Daily Quiz Frontend Views

@login_required
def daily_quiz_view(request):
    user = request.user
    today = localdate()

    quiz_questions = DailyQuiz.objects.filter(quiz_date=today).order_by('id')

    if not quiz_questions.exists():
        context = {
            'no_quiz_today': True,
            'quiz_questions_json': json.dumps([]),
            'quiz_submitted': False,
            'score': None,
            'percent': None,
            'total_questions': 0,
            'today': today.strftime('%Y-%m-%d'),
        }
        return render(request, 'dailyquiz.html', context)

    attempt = DailyQuizAttempt.objects.filter(user=user, quiz_date=today).first()
    quiz_submitted = attempt is not None

    quiz_questions_data = []
    for q in quiz_questions:
        correct_options = ['A', 'B', 'C', 'D']
        try:
            correct_index = correct_options.index((q.correct_option or '').upper())
        except (ValueError, AttributeError):
            correct_index = 0

        quiz_questions_data.append({
            "id": q.id,
            "question": q.question,
            "answers": [q.option_a, q.option_b, q.option_c, q.option_d],
            "correctIndex": correct_index,
        })

    context = {
        'no_quiz_today': False,
        'quiz_questions_json': json.dumps(quiz_questions_data),
        'quiz_submitted': quiz_submitted,
        'score': attempt.score if attempt else None,
        'percent': attempt.percent if attempt else None,
        'total_questions': quiz_questions.count(),
        'user_answers': attempt.answers if attempt else None,
        'today': today.strftime('%Y-%m-%d'),
        'attempt_id': attempt.id if attempt else None,
        'attempted_on': attempt.quiz_date.strftime('%Y-%m-%d %H:%M:%S') if attempt else None,
    }
    return render(request, 'dailyquiz.html', context)


@login_required
def submit_daily_quiz(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    user = request.user
    today = localdate()

    quiz_questions = DailyQuiz.objects.filter(quiz_date=today).order_by('id')
    if not quiz_questions.exists():
        return JsonResponse({'error': 'No quiz available for today.'}, status=400)

    if DailyQuizAttempt.objects.filter(user=user, quiz_date=today).exists():
        return JsonResponse({'error': 'Quiz already attempted today.'}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
        answers = data.get('answers', [])
    except Exception as e:
        return JsonResponse({'error': 'Invalid JSON data.', 'details': str(e)}, status=400)

    score = 0
    total_questions = quiz_questions.count()
    correct_answers = []

    for idx, question in enumerate(quiz_questions):
        correct_opt = (question.correct_option or '').upper()
        correct_answers.append(correct_opt)

        user_answer = answers[idx].upper() if idx < len(answers) and answers[idx] else None
        if user_answer == correct_opt:
            score += 1

    percent = int((score / total_questions) * 100) if total_questions else 0

    try:
        attempt = DailyQuizAttempt.objects.create(
            user=user,
            quiz_date=today,
            score=score,
            percent=percent,
            answers=answers,
        )
    except Exception as exc:
        import traceback
        print(f"Error saving DailyQuizAttempt: {traceback.format_exc()}")
        return JsonResponse({'error': 'Failed to save attempt.', 'details': str(exc)}, status=500)

    return JsonResponse({
        'success': True,
        'score': score,
        'percent': percent,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'attempt_id': attempt.id,
    })


# Authentication API Views

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'detail': 'All fields are required.'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'username': ['A user with that username already exists.']}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({'email': ['A user with that email already exists.']}, status=400)

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'password': e.messages}, status=400)

        user = User(username=username, email=email)
        user.set_password(password)
        user.save()

        return Response({'detail': 'User registered successfully'}, status=201)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'detail': 'Login successful'}, status=200)
        else:
            return Response({'detail': 'Invalid credentials'}, status=401)

# Frontend Render Views

@ensure_csrf_cookie
def home_view(request):
    return render(request, 'index.html')

@ensure_csrf_cookie
def login_view(request):
    return render(request, 'login.html')

@ensure_csrf_cookie
def register_view(request):
    return render(request, 'register.html')

@ensure_csrf_cookie
def syllabus_view(request):
    return render(request, 'syllabus.html')

@ensure_csrf_cookie
def mock_tests_view(request):
    return render(request, 'mocktest.html')

@ensure_csrf_cookie
def previous_papers_view(request):
    return render(request, 'previouspaper.html')

@ensure_csrf_cookie
def results_view(request):
    return render(request, 'results.html')

@ensure_csrf_cookie
def keywords_view(request):
    return render(request, 'keywords.html')

@ensure_csrf_cookie
def interview_questions(request):
    return render(request, 'interview.html')

@ensure_csrf_cookie
def formula_view(request):
    formulas = Formula.objects.all()
    return render(request, 'formula.html', {'formulas': formulas})

@login_required
def ai_chat_view(request):
    return render(request, 'aichat.html')

# AI Chat History API Views

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def save_ai_chat_history(request):
    user = request.user
    if request.method == 'POST':
        user_message = request.data.get('user')
        ai_response = request.data.get('ai')
        if user_message is not None and ai_response is not None:
            history = AIChatHistory.objects.create(
                user=user,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "ai", "content": ai_response},
                ]
            )
            return Response({'status': 'ok'})
        return Response({'status': 'fail', "detail": "Missing user or ai message."}, status=400)
    elif request.method == 'GET':
        chats = AIChatHistory.objects.filter(user=user).order_by('-timestamp')[:20]
        return Response([
            {
                'id': chat.pk,
                'conversation_id': chat.conversation_id,
                'messages': chat.messages
            }
            for chat in chats
        ])


class DeleteAIChatHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, chat_id):
        try:
            chat = AIChatHistory.objects.get(id=chat_id, user=request.user)
            chat.delete()
            return Response({"success": True}, status=204)
        except AIChatHistory.DoesNotExist:
            return Response({"error": "Chat not found"}, status=404)


class CrackItAIChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get("message")
        if not user_message:
            return Response({"error": "No message provided"}, status=400)
        try:
            # TODO: implement AI inference here
            answer = "AI response placeholder - implement inference here."
            return Response({"answer": answer})
        except Exception as e:
            import traceback
            print("AI chat view error:", traceback.format_exc())
            return Response({"error": str(e)}, status=500)
