#!/usr/bin/env python
"""
Test script for the improved course generation with better video controls and study notes
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coursegen.settings')
django.setup()

from courses.services import CourseGenerationService
from courses.models import Course, Lesson, StudyNote, Module

def test_improved_course_generation():
    """Test the improved course generation with better structure"""
    print("Testing improved course generation...")
    
    # Create service
    service = CourseGenerationService()
    
    # Test with a YouTube URL
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    
    try:
        # Generate course
        print(f"Generating course from: {youtube_url}")
        course = service.generate_course(
            youtube_url=youtube_url,
            topic="Python Programming",
            difficulty="beginner"
        )
        
        print(f"✅ Course created: {course.title}")
        print(f"   ID: {course.id}")
        print(f"   Modules: {course.modules.count()}")
        
        # Check for improved structure
        total_lessons = 0
        study_notes_lessons = 0
        video_lessons = 0
        
        for module in course.modules.all():
            print(f"\n📚 Module: {module.title}")
            module_video_lessons = 0
            module_study_notes = 0
            
            for lesson in module.lessons.all():
                total_lessons += 1
                print(f"   📝 Lesson: {lesson.title} (Type: {lesson.lesson_type})")
                
                if lesson.lesson_type == 'notes':
                    study_notes_lessons += 1
                    module_study_notes += 1
                    try:
                        study_note = lesson.study_note
                        print(f"      ✅ Study notes found: {len(study_note.content)} characters")
                        print(f"      📋 Key concepts: {len(study_note.key_concepts)}")
                        print(f"      💻 Code examples: {len(study_note.code_examples)}")
                        print(f"      📝 Summary: {len(study_note.summary)} characters")
                        print(f"      🎯 Module-level notes: {'Complete Study Guide' in lesson.title}")
                    except StudyNote.DoesNotExist:
                        print(f"      ❌ No study notes found")
                elif lesson.lesson_type == 'video':
                    video_lessons += 1
                    module_video_lessons += 1
                    if lesson.chapter_timestamp:
                        print(f"      ⏰ Timestamp: {lesson.chapter_timestamp}")
                elif lesson.lesson_type == 'quiz':
                    print(f"      🎯 Quiz lesson")
            
            # Verify module structure
            print(f"      📊 Module stats: {module_video_lessons} videos, {module_study_notes} study notes")
            if module_study_notes == 1:
                print(f"      ✅ Correct: One study note per module")
            else:
                print(f"      ❌ Issue: {module_study_notes} study notes in module")
        
        print(f"\n📊 Summary:")
        print(f"   Total lessons: {total_lessons}")
        print(f"   Video lessons: {video_lessons}")
        print(f"   Study notes lessons: {study_notes_lessons}")
        print(f"   Modules: {course.modules.count()}")
        
        # Test API endpoints
        print(f"\n🔗 API Endpoints:")
        print(f"   Course detail: /api/courses/{course.id}/")
        
        # Find a study notes lesson for testing
        study_notes_lesson = None
        for module in course.modules.all():
            for lesson in module.lessons.all():
                if lesson.lesson_type == 'notes':
                    study_notes_lesson = lesson
                    break
            if study_notes_lesson:
                break
        
        if study_notes_lesson:
            print(f"   Study notes: /api/lessons/{study_notes_lesson.id}/study-notes/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating course: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_improved_course_generation()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1) 