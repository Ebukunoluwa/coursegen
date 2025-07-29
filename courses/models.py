from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import re

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    youtube_source = models.URLField(blank=True, null=True)  # Single video URL
    playlist_url = models.URLField(blank=True, null=True)    # Playlist URL
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    generation_type = models.CharField(max_length=20, choices=[
        ('link', 'YouTube Link'),
        ('prompt', 'AI Prompt'),
        ('topic', 'Topic Only')
    ], default='link')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_playlist_id(self):
        """Extract playlist ID from playlist URL"""
        if not self.playlist_url:
            return None
        
        # Match playlist ID from various YouTube playlist URL formats
        patterns = [
            r'(?:youtube\.com/playlist\?list=|youtube\.com/watch\?.*&list=)([^&]+)',
            r'(?:youtube\.com/playlist\?list=)([^&]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.playlist_url)
            if match:
                return match.group(1)
        return None
    
    def is_playlist(self):
        """Check if this course is based on a playlist"""
        return bool(self.playlist_url)
    
    def get_video_count(self):
        """Get total number of videos in the course"""
        total = 0
        for module in self.modules.all():
            total += module.lessons.count()
        return total

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    video_id = models.CharField(max_length=20, blank=True, null=True)  # Video ID for this module
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    LESSON_TYPES = [
        ('video', 'Video Lesson'),
        ('notes', 'Study Notes'),
        ('quiz', 'Quiz'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPES, default='video')
    youtube_video_id = models.CharField(max_length=20, blank=True, null=True)
    ai_notes = models.TextField(blank=True)
    duration = models.IntegerField(default=0)  # in seconds
    order = models.IntegerField(default=0)
    chapter_timestamp = models.CharField(max_length=10, blank=True, null=True)  # Format: "MM:SS" or "HH:MM:SS"
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    def get_timestamp_seconds(self):
        """Convert chapter_timestamp to seconds for video navigation"""
        if not self.chapter_timestamp:
            return 0
        
        parts = self.chapter_timestamp.split(':')
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        return 0
    
    def is_study_notes(self):
        """Check if this lesson is a study notes lesson"""
        return self.lesson_type == 'notes'
    
    def is_video_lesson(self):
        """Check if this lesson is a video lesson"""
        return self.lesson_type == 'video'

class StudyNote(models.Model):
    """Enhanced study notes with 3 types: Golden Notes, Summaries, and Own Notes"""
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='study_note')
    
    # Golden Notes - Deep, comprehensive explanations
    golden_notes = models.JSONField(default=list)  # List of concept cards with detailed explanations
    
    # Summaries - Quick, scannable bullet points
    summaries = models.JSONField(default=list)  # List of key concept summaries
    
    # Own Notes - User-editable personal notes
    own_notes = models.TextField(blank=True, default="")  # User's personal notes
    
    # Legacy field for backward compatibility
    content = models.TextField(blank=True)  # Markdown formatted content
    key_concepts = models.JSONField(default=list)  # List of key concepts
    code_examples = models.JSONField(default=list)  # List of code examples
    summary = models.TextField(blank=True)  # Quick summary
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Study Notes for {self.lesson.title}"
    
    def get_formatted_content(self):
        """Get formatted content for backward compatibility"""
        return self.content
    
    def get_golden_notes_cards(self):
        """Get golden notes as concept cards"""
        return self.golden_notes or []
    
    def get_summaries_list(self):
        """Get summaries as bullet points"""
        return self.summaries or []
    
    def get_own_notes(self):
        """Get user's personal notes"""
        return self.own_notes or ""

class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    questions = models.JSONField(default=list)  # List of question objects
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Quiz for {self.lesson.title}"

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    completed = models.BooleanField(default=False)
    quiz_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, 
        blank=True
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"
