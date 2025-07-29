#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coursegen.settings')
django.setup()

from courses.services import CourseGenerationService

def generate_course_from_url(youtube_url):
    """Generate a course with dynamic notes from any YouTube URL"""
    
    print(f"🎬 Generating dynamic notes from: {youtube_url}")
    print("⏳ This may take a few moments...")
    
    try:
        service = CourseGenerationService()
        course = service.generate_course(youtube_url=youtube_url)
        
        print(f"\n✅ Course generated successfully!")
        print(f"📚 Course title: {course.title}")
        print(f"📖 Number of modules: {course.modules.count()}")
        
        # Show the study notes
        for module in course.modules.all():
            print(f"\n📋 Module: {module.title}")
            for lesson in module.lessons.all():
                if lesson.lesson_type == 'notes':
                    print(f"  📝 Study Notes: {lesson.title}")
                    if hasattr(lesson, 'study_note'):
                        study_note = lesson.study_note
                        print(f"    ✨ Golden notes: {len(study_note.golden_notes)}")
                        print(f"    📝 Summaries: {len(study_note.summaries)}")
                        
                        if study_note.golden_notes:
                            print(f"    🏆 First golden note: {study_note.golden_notes[0]['title']}")
                        
                        if study_note.summaries:
                            print(f"    📌 First summary: {study_note.summaries[0][:80]}...")
        
        print(f"\n🎉 Dynamic notes generated successfully!")
        print(f"💡 You can now view the course in your application to see the beautiful Alice.tech-style interface!")
        
        return course
        
    except Exception as e:
        print(f"❌ Error generating course: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        youtube_url = sys.argv[1]
        generate_course_from_url(youtube_url)
    else:
        print("Usage: python test_any_url.py <youtube_url>")
        print("Example: python test_any_url.py https://www.youtube.com/watch?v=example")
        
        # Test with a default educational video
        test_url = "https://www.youtube.com/watch?v=8jLoD7aJt6E"  # Python tutorial
        print(f"\n🧪 Testing with default URL: {test_url}")
        generate_course_from_url(test_url) 