from django.contrib import admin
from .models import Course, Module, Lesson, Quiz, UserProgress, StudyNote

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'created_at', 'is_playlist', 'get_video_count']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'course__title']
    ordering = ['course', 'order']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'order', 'duration', 'created_at']
    list_filter = ['lesson_type', 'module__course', 'created_at']
    search_fields = ['title', 'module__title', 'module__course__title']
    ordering = ['module', 'order']
    readonly_fields = ['created_at']

@admin.register(StudyNote)
class StudyNoteAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'summary', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['lesson__title', 'summary']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'created_at']
    list_filter = ['created_at']
    search_fields = ['lesson__title']
    readonly_fields = ['created_at']

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'quiz_score', 'completed_at']
    list_filter = ['completed', 'completed_at', 'lesson__module__course']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['completed_at']
