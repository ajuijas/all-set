from django.urls import path

from . import views

urlpatterns = [
    path('api/generate-questions/', views.GenerateQuestionsAPIView.as_view(), name='generate_questions'),
    path('api/evaluate-answer/', views.GetResultsAPIView.as_view(), name='evaluate_answer'),
    path('', views.upload_page, name='upload_page'),
    path('questions-page/', views.questions_page, name='questions_page'),
]