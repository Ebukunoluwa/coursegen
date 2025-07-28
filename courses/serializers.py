from rest_framework import serializers
from .models import Course, Module, Lesson, Quiz, UserProgress

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'questions', 'created_at']

class LessonSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'youtube_video_id', 'ai_notes', 'duration', 'order', 'chapter_timestamp', 'quiz', 'created_at']

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'lessons', 'created_at']

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'youtube_source', 'difficulty', 'modules', 'created_at', 'updated_at']

class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    module_title = serializers.CharField(source='lesson.module.title', read_only=True)
    course_title = serializers.CharField(source='lesson.module.course.title', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = ['id', 'lesson', 'lesson_title', 'module_title', 'course_title', 'completed', 'quiz_score', 'completed_at']

class CourseGenerationRequestSerializer(serializers.Serializer):
    youtube_url = serializers.URLField(required=False, allow_blank=True)
    topic = serializers.CharField(required=False, allow_blank=True)
    difficulty = serializers.ChoiceField(choices=Course.DIFFICULTY_CHOICES, default='beginner')
    
    def validate(self, data):
        if not data.get('youtube_url') and not data.get('topic'):
            raise serializers.ValidationError("Either youtube_url or topic must be provided")
        return data 