from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Course, Module, Lesson, Quiz, UserProgress
from .serializers import (
    CourseSerializer, ModuleSerializer, LessonSerializer, 
    QuizSerializer, UserProgressSerializer, CourseGenerationRequestSerializer
)
from .services import CourseGenerationService
from django.db import models

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_course(request):
    """Generate a new course from YouTube URL or topic"""
    print(f"Request method: {request.method}")
    print(f"Request content type: {request.content_type}")
    print(f"Request data: {request.data}")
    
    serializer = CourseGenerationRequestSerializer(data=request.data)
    if serializer.is_valid():
        try:
            print(f"Validated data: {serializer.validated_data}")
            service = CourseGenerationService()
            course = service.generate_course(
                youtube_url=serializer.validated_data.get('youtube_url'),
                topic=serializer.validated_data.get('topic'),
                difficulty=serializer.validated_data.get('difficulty', 'beginner')
            )
            
            course_serializer = CourseSerializer(course)
            return Response(course_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error generating course: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        print(f"Serializer errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request):
    """Get all courses"""
    courses = Course.objects.all().order_by('-created_at')
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def course_detail(request, course_id):
    """Get detailed course information"""
    course = get_object_or_404(Course, id=course_id)
    serializer = CourseSerializer(course)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_course(request, course_id):
    """Delete a course"""
    try:
        course = get_object_or_404(Course, id=course_id)
        course.delete()
        return Response({'message': 'Course deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response(
            {'error': f'Error deleting course: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def module_detail(request, module_id):
    """Get detailed module information"""
    module = get_object_or_404(Module, id=module_id)
    serializer = ModuleSerializer(module)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def lesson_detail(request, lesson_id):
    """Get detailed lesson information"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    serializer = LessonSerializer(lesson)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def quiz_detail(request, lesson_id):
    """Get quiz for a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    quiz = get_object_or_404(Quiz, lesson=lesson)
    serializer = QuizSerializer(quiz)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_quiz(request, lesson_id):
    """Submit quiz answers and get score"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    quiz = get_object_or_404(Quiz, lesson=lesson)
    
    answers = request.data.get('answers', [])
    if not answers:
        return Response(
            {'error': 'Answers are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate score
    correct_answers = 0
    total_questions = len(quiz.questions)
    
    for i, answer in enumerate(answers):
        if i < total_questions and answer == quiz.questions[i].get('correct_answer'):
            correct_answers += 1
    
    score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    
    # Create or update user progress
    user_id = request.data.get('user_id', 1)  # Default user for demo
    user, created = User.objects.get_or_create(id=user_id, defaults={'username': f'user_{user_id}'})
    
    progress, created = UserProgress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={'completed': True, 'quiz_score': score}
    )
    
    if not created:
        progress.quiz_score = score
        progress.completed = True
        progress.save()
    
    return Response({
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'completed': True
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def user_progress(request, user_id):
    """Get user progress for all courses"""
    user = get_object_or_404(User, id=user_id)
    progress = UserProgress.objects.filter(user=user).order_by('-completed_at')
    serializer = UserProgressSerializer(progress, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def mark_lesson_completed(request, lesson_id):
    """Mark a lesson as completed"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user_id = request.data.get('user_id', 1)
    user, created = User.objects.get_or_create(id=user_id, defaults={'username': f'user_{user_id}'})
    
    progress, created = UserProgress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={'completed': True}
    )
    
    if not created:
        progress.completed = True
        progress.save()
    
    return Response({'status': 'completed'})

@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_stats(request, user_id):
    """Get dashboard statistics for a user"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user progress
    progress = UserProgress.objects.filter(user=user)
    completed_lessons = progress.filter(completed=True).count()
    total_lessons = Lesson.objects.count()
    average_score = progress.filter(quiz_score__isnull=False).aggregate(
        avg_score=models.Avg('quiz_score')
    )['avg_score'] or 0
    
    # Get active courses (courses with at least one completed lesson)
    active_courses = Course.objects.filter(
        modules__lessons__user_progress__user=user,
        modules__lessons__user_progress__completed=True
    ).distinct()
    
    return Response({
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'completion_percentage': int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0,
        'average_score': round(average_score, 1),
        'active_courses': CourseSerializer(active_courses, many=True).data
    })
