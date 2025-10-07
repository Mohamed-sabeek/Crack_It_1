from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from core import views
from core.views import (
    home_view,
    login_view,
    register_view,
    syllabus_view,
    mock_tests_view,
    previous_papers_view,
    results_view,
    keywords_view,
    interview_questions,
    formula_view,
    ai_chat_view,
    SyllabusViewSet,
    PreviousPaperViewSet,
    KeywordViewSet,
    InterviewQuestionViewSet,
    MockTestViewSet,
    FormulaViewSet,
    QuestionListAPIView,
    SubmitTestAPIView,
    TestAttemptListAPIView,
    TestAttemptDetailAPIView,
    RegisterAPIView,
    LoginAPIView,
)

from core.views_ai import CrackItAIChatAPIView, DeleteAIChatHistoryAPIView
from core.views import save_ai_chat_history

from rest_framework import routers

# DRF router for readonly viewsets
router = routers.DefaultRouter()
router.register(r'syllabus', SyllabusViewSet)
router.register(r'previous-papers', PreviousPaperViewSet)
router.register(r'keywords', KeywordViewSet)
router.register(r'interview-questions', InterviewQuestionViewSet)
router.register(r'mock-tests', MockTestViewSet)
router.register(r'formulas', FormulaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),

    path('api/auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/auth/login/', LoginAPIView.as_view(), name='api-login'),

    path('api/mock-tests/<int:test_id>/questions/', QuestionListAPIView.as_view(), name='mocktest-questions'),
    path('api/mock-tests/<int:test_id>/submit/', SubmitTestAPIView.as_view(), name='mocktest-submit'),

    path('api/user/test-attempts/', TestAttemptListAPIView.as_view(), name='user-test-attempts'),
    path('api/user/test-attempts/<int:attempt_id>/details/', TestAttemptDetailAPIView.as_view(), name='test-attempt-detail'),

    # Frontend pages rendering
    path('', TemplateView.as_view(template_name='auth.html'), name='landing'),
    path('index.html', home_view, name='home'),
    path('login.html', login_view, name='login'),
    path('register.html', register_view, name='register'),
    path('syllabus.html', syllabus_view, name='syllabus'),
    path('mocktest.html', mock_tests_view, name='mocktest'),
    path('previouspaper.html', previous_papers_view, name='previouspaper'),
    path('results.html', results_view, name='results'),
    path('keywords.html', keywords_view, name='keywords'),
    path('dailyquiz.html', views.daily_quiz_view, name='dailyquiz'),
    path('interview.html', interview_questions, name='interview'),
    path('formula.html', formula_view, name='formula'),
    path('aichat.html', ai_chat_view, name='aichat'),
    path('submit-daily-quiz/', views.submit_daily_quiz, name='submit_daily_quiz'),


    path('api/ai-chat/', CrackItAIChatAPIView.as_view(), name='api-ai-chat'),

    path('api/ai-chat-history/', save_ai_chat_history, name='ai-chat-history'),
    path('api/ai-chat-history/<int:chat_id>/', DeleteAIChatHistoryAPIView.as_view(), name='delete-ai-chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
