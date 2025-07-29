from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Course, Module, Lesson, Quiz, UserProgress, StudyNote
from .serializers import (
    CourseSerializer, ModuleSerializer, LessonSerializer, 
    QuizSerializer, UserProgressSerializer, CourseGenerationRequestSerializer,
    StudyNoteSerializer
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
                difficulty=serializer.validated_data.get('difficulty', 'beginner'),
                prompt=serializer.validated_data.get('prompt'),
                generation_type=serializer.validated_data.get('generation_type', 'link')
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
def study_notes_detail(request, lesson_id):
    """Get enhanced study notes for a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not lesson.is_study_notes():
        return Response(
            {'error': 'This lesson does not have study notes'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if regeneration is requested
    regenerate = request.GET.get('regenerate', False)
    
    # Get or create study notes
    study_note, created = StudyNote.objects.get_or_create(lesson=lesson)
    
    # If newly created or regeneration requested, generate the notes
    if created or regenerate:
        from .services import AIService
        ai_service = AIService()
        video_info = None
        if lesson.youtube_video_id:
            from .services import YouTubeService
            yt_service = YouTubeService()
            video_info = yt_service.get_video_info(lesson.youtube_video_id)
        
        enhanced_notes = ai_service.generate_structured_study_notes(
            lesson.title, 
            video_info=video_info
        )
        
        # Update the study note with enhanced content
        study_note.golden_notes = enhanced_notes.get('golden_notes', [])
        study_note.summaries = enhanced_notes.get('summaries', [])
        study_note.content = enhanced_notes.get('content', '')
        study_note.key_concepts = enhanced_notes.get('key_concepts', [])
        study_note.code_examples = enhanced_notes.get('code_examples', [])
        study_note.summary = enhanced_notes.get('summary', '')
        study_note.save()
    
    serializer = StudyNoteSerializer(study_note)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def update_own_notes(request, lesson_id):
    """Update user's own notes for a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not lesson.is_study_notes():
        return Response(
            {'error': 'This lesson does not have study notes'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or create study notes
    study_note, created = StudyNote.objects.get_or_create(lesson=lesson)
    
    # Update own notes
    from .serializers import OwnNotesUpdateSerializer
    serializer = OwnNotesUpdateSerializer(study_note, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def quiz_detail(request, lesson_id):
    """Get quiz for a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not lesson.lesson_type == 'quiz':
        return Response(
            {'error': 'This lesson is not a quiz lesson'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        quiz = Quiz.objects.get(lesson=lesson)
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found for this lesson'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_quiz(request, lesson_id):
    """Submit quiz answers and get score"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not lesson.lesson_type == 'quiz':
        return Response(
            {'error': 'This lesson is not a quiz lesson'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        quiz = Quiz.objects.get(lesson=lesson)
    except Quiz.DoesNotExist:
        return Response(
            {'error': 'Quiz not found for this lesson'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
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
