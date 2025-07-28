from django.urls import path
from . import views

urlpatterns = [
    # Course generation and listing
    path('generate/', views.generate_course, name='generate_course'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    
    # Module and lesson details
    path('modules/<int:module_id>/', views.module_detail, name='module_detail'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    
    # Quiz functionality
    path('lessons/<int:lesson_id>/quiz/', views.quiz_detail, name='quiz_detail'),
    path('lessons/<int:lesson_id>/submit-quiz/', views.submit_quiz, name='submit_quiz'),
    
    # Progress tracking
    path('users/<int:user_id>/progress/', views.user_progress, name='user_progress'),
    path('lessons/<int:lesson_id>/complete/', views.mark_lesson_completed, name='mark_lesson_completed'),
    path('users/<int:user_id>/dashboard/', views.dashboard_stats, name='dashboard_stats'),
] 