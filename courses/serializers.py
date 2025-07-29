from rest_framework import serializers
from .models import Course, Module, Lesson, Quiz, UserProgress, StudyNote

class StudyNoteSerializer(serializers.ModelSerializer):
    golden_notes_cards = serializers.SerializerMethodField()
    summaries_list = serializers.SerializerMethodField()
    
    class Meta:
        model = StudyNote
        fields = [
            'id', 'golden_notes', 'summaries', 'own_notes', 
            'golden_notes_cards', 'summaries_list',
            'content', 'key_concepts', 'code_examples', 'summary', 
            'created_at', 'updated_at'
        ]
    
    def get_golden_notes_cards(self, obj):
        return obj.get_golden_notes_cards()
    
    def get_summaries_list(self, obj):
        return obj.get_summaries_list()

class OwnNotesUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user's own notes"""
    
    class Meta:
        model = StudyNote
        fields = ['own_notes']
    
    def update(self, instance, validated_data):
        instance.own_notes = validated_data.get('own_notes', instance.own_notes)
        instance.save()
        return instance

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'questions', 'created_at']

class LessonSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    study_note = StudyNoteSerializer(read_only=True)
    lesson_type_display = serializers.CharField(source='get_lesson_type_display', read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'lesson_type', 'lesson_type_display', 'youtube_video_id', 
            'ai_notes', 'duration', 'order', 'chapter_timestamp', 'quiz', 'study_note', 'created_at'
        ]

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'video_id', 'lessons', 'created_at']

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    is_playlist = serializers.SerializerMethodField()
    video_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'youtube_source', 'playlist_url', 'difficulty', 'generation_type', 'modules', 'is_playlist', 'video_count', 'created_at', 'updated_at']
    
    def get_is_playlist(self, obj):
        return obj.is_playlist()
    
    def get_video_count(self, obj):
        return obj.get_video_count()

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
    prompt = serializers.CharField(required=False, allow_blank=True)
    difficulty = serializers.ChoiceField(choices=Course.DIFFICULTY_CHOICES, default='beginner')
    generation_type = serializers.CharField(required=False, default='link')
    
    def validate(self, data):
        if not data.get('youtube_url') and not data.get('topic') and not data.get('prompt'):
            raise serializers.ValidationError("Either youtube_url, topic, or prompt must be provided")
        return data 