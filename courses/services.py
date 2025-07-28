import re
import requests
import openai
from django.conf import settings
from .models import Course, Module, Lesson, Quiz

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
    
    def extract_video_id(self, url):
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_info(self, video_id):
        """Get video information from YouTube API"""
        if not self.api_key:
            return None
            
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,contentDetails',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['items']:
                video = data['items'][0]
                return {
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'duration': self._parse_duration(video['contentDetails']['duration']),
                    'channel': video['snippet']['channelTitle']
                }
        except Exception as e:
            print(f"Error fetching YouTube video info: {e}")
        
        return None
    
    def get_video_transcript(self, video_id):
        """Get video transcript using YouTube Data API"""
        if not self.api_key:
            return None
            
        # First, get the caption tracks
        url = "https://www.googleapis.com/youtube/v3/captions"
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['items']:
                # Get the first available transcript (usually English)
                caption_id = data['items'][0]['id']
                
                # Download the transcript
                transcript_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}"
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Accept': 'application/json'
                }
                
                transcript_response = requests.get(transcript_url, headers=headers)
                if transcript_response.status_code == 200:
                    return transcript_response.text
                    
        except Exception as e:
            print(f"Error fetching video transcript: {e}")
        
        return None
    
    def extract_chapters_from_description(self, description):
        """Extract chapters from video description"""
        chapters = []
        lines = description.split('\n')
        
        for line in lines:
            # Look for timestamp patterns like "1:23 Chapter Title" or "01:23 Chapter Title"
            timestamp_match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)', line.strip())
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                title = timestamp_match.group(2).strip()
                if title and len(title) > 3:  # Filter out very short titles
                    chapters.append({
                        'timestamp': timestamp,
                        'title': title,
                        'seconds': self._timestamp_to_seconds(timestamp)
                    })
        
        return chapters
    
    def generate_chapters_from_transcript(self, transcript, video_duration):
        """Generate chapters from transcript using AI"""
        if not transcript or not settings.OPENAI_API_KEY:
            return []
        
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            prompt = f"""
            Analyze this video transcript and create logical chapters with timestamps.
            Video duration: {video_duration} seconds
            
            Transcript:
            {transcript[:2000]}...
            
            Create 5-8 chapters with timestamps in this format:
            - 00:00 Introduction
            - 02:30 Main Topic 1
            - 05:15 Main Topic 2
            etc.
            
            Return only the chapters in the format above, no additional text.
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            chapters_text = response.choices[0].message.content.strip()
            return self._parse_ai_generated_chapters(chapters_text)
            
        except Exception as e:
            print(f"Error generating chapters from transcript: {e}")
            return []
    
    def _parse_ai_generated_chapters(self, chapters_text):
        """Parse AI-generated chapters text into structured format"""
        chapters = []
        lines = chapters_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                line = line[1:].strip()
            
            timestamp_match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)', line)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                title = timestamp_match.group(2).strip()
                if title and len(title) > 3:
                    chapters.append({
                        'timestamp': timestamp,
                        'title': title,
                        'seconds': self._timestamp_to_seconds(timestamp)
                    })
        
        return chapters
    
    def _timestamp_to_seconds(self, timestamp):
        """Convert timestamp (HH:MM:SS or MM:SS) to seconds"""
        parts = timestamp.split(':')
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        return 0
    
    def _parse_duration(self, duration_str):
        """Parse ISO 8601 duration to seconds"""
        import re
        match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration_str)
        if not match:
            return 0
        
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        seconds = int(match.group(3)[:-1]) if match.group(3) else 0
        
        return hours * 3600 + minutes * 60 + seconds

class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
    
    def generate_course_structure(self, topic, video_info=None, difficulty='beginner', chapters=None):
        """Generate course structure with AI notes included"""
        if not self.client:
            return self._generate_mock_structure(topic, difficulty, chapters)
            
        prompt_parts = [
            f"Generate a comprehensive course structure for '{topic}' at {difficulty} level."
        ]
        
        if video_info:
            prompt_parts.append(f"Based on the video: {video_info.get('title', 'Unknown')}")
            if video_info.get('description'):
                prompt_parts.append(f"Video description: {video_info['description'][:500]}...")
        
        if chapters:
            prompt_parts.append("Use these video chapters to structure the course:")
            for chapter in chapters[:8]:  # Limit to 8 chapters
                prompt_parts.append(f"- {chapter['timestamp']}: {chapter['title']}")
        
        prompt = "\n".join(prompt_parts) + """
        
        Generate a complete course structure with:
        1. Course title and description
        2. 3-5 modules, each with 2-4 lessons
        3. Each lesson should have a title, brief description, AND comprehensive AI notes
        4. Include quiz questions for each lesson (3-5 multiple choice questions)
        
        For each lesson, include detailed AI notes covering:
        - Key concepts and definitions
        - Important points to remember
        - Examples and explanations
        - Practical tips and best practices
        
        Format as JSON:
        {
            "title": "Course Title",
            "description": "Course description",
            "modules": [
                {
                    "title": "Module Title",
                    "lessons": [
                        {
                            "title": "Lesson Title",
                            "description": "Lesson description",
                            "ai_notes": "Comprehensive AI-generated notes for this lesson including key concepts, examples, and best practices...",
                            "quiz_questions": [
                                {
                                    "question": "Question text",
                                    "options": ["A", "B", "C", "D"],
                                    "correct_answer": 0
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating course structure: {e}")
            return self._generate_mock_structure(topic, difficulty, chapters)
    
    def generate_lesson_notes(self, lesson_title, video_transcript=None):
        """Generate AI notes for a lesson"""
        if not self.client:
            return f"AI-generated notes for {lesson_title}. This would contain key points, summaries, and additional context."
        
        prompt = f"""
        Generate comprehensive notes for the lesson: "{lesson_title}"
        
        {f"Based on this video transcript: {video_transcript[:1000]}..." if video_transcript else ""}
        
        Include:
        - Key concepts and definitions
        - Important points to remember
        - Examples and explanations
        - Practical tips and best practices
        
        Format as clear, structured notes.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating lesson notes: {e}")
            return f"AI-generated notes for {lesson_title}. This would contain key points, summaries, and additional context."
    
    def _generate_mock_structure(self, topic, difficulty, chapters=None):
        """Generate mock course structure when OpenAI is not available"""
        if chapters:
            # Use chapters to create more realistic structure
            modules = []
            current_module = {
                "title": f"Introduction to {topic}",
                "lessons": []
            }
            
            for i, chapter in enumerate(chapters[:8]):  # Limit to 8 chapters
                if i > 0 and i % 3 == 0:  # Start new module every 3 lessons
                    modules.append(current_module)
                    current_module = {
                        "title": f"Module {len(modules) + 2}",
                        "lessons": []
                    }
                
                current_module["lessons"].append({
                    "title": chapter['title'],
                    "description": f"Learn about {chapter['title'].lower()}",
                    "ai_notes": f"AI-generated notes for {chapter['title']}. This lesson covers key concepts, important points, examples, and practical tips related to {chapter['title'].lower()}.",
                    "quiz_questions": [
                        {
                            "question": f"What is the main topic of {chapter['title']}?",
                            "options": ["A", "B", "C", "D"],
                            "correct_answer": 0
                        }
                    ]
                })
            
            if current_module["lessons"]:
                modules.append(current_module)
        else:
            # Fallback to generic structure
            modules = [
                {
                    "title": f"Introduction to {topic}",
                    "lessons": [
                        {
                            "title": f"Getting Started with {topic}",
                            "description": f"Learn the basics of {topic} and set up your development environment.",
                            "ai_notes": f"AI-generated notes for Getting Started with {topic}. This lesson covers key concepts, important points, examples, and practical tips for beginners.",
                            "quiz_questions": [
                                {
                                    "question": f"What is {topic}?",
                                    "options": ["A programming language", "A framework", "A tool", "All of the above"],
                                    "correct_answer": 3
                                }
                            ]
                        },
                        {
                            "title": f"Core Concepts of {topic}",
                            "description": f"Understand the fundamental concepts and principles of {topic}.",
                            "ai_notes": f"AI-generated notes for Core Concepts of {topic}. This lesson covers fundamental principles, key definitions, and essential concepts.",
                            "quiz_questions": [
                                {
                                    "question": f"Which of the following is a key feature of {topic}?",
                                    "options": ["Speed", "Simplicity", "Flexibility", "All of the above"],
                                    "correct_answer": 3
                                }
                            ]
                        }
                    ]
                },
                {
                    "title": f"Advanced {topic} Techniques",
                    "lessons": [
                        {
                            "title": f"Advanced Features in {topic}",
                            "description": f"Explore advanced features and techniques in {topic}.",
                            "ai_notes": f"AI-generated notes for Advanced Features in {topic}. This lesson covers advanced techniques, best practices, and expert tips.",
                            "quiz_questions": [
                                {
                                    "question": f"What is the best practice for {topic}?",
                                    "options": ["Follow conventions", "Use best practices", "Write clean code", "All of the above"],
                                    "correct_answer": 3
                                }
                            ]
                        }
                    ]
                }
            ]
        
        return {
            "title": f"Learn {topic} - {difficulty.title()} Course",
            "description": f"A comprehensive course on {topic} designed for {difficulty} level learners.",
            "modules": modules
        }

class CourseGenerationService:
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.ai_service = AIService()
    
    def generate_course(self, youtube_url=None, topic=None, difficulty='beginner'):
        """Generate a course from YouTube URL or topic"""
        if not youtube_url and not topic:
            raise ValueError("Either youtube_url or topic must be provided")
        
        video_info = None
        chapters = []
        video_id = None
        
        if youtube_url:
            video_id = self.youtube_service.extract_video_id(youtube_url)
            if video_id:
                video_info = self.youtube_service.get_video_info(video_id)
                
                if video_info:
                    # Extract chapters from description first
                    chapters = self.youtube_service.extract_chapters_from_description(video_info.get('description', ''))
                    
                    # If no chapters in description, try to get transcript and generate chapters
                    if not chapters:
                        transcript = self.youtube_service.get_video_transcript(video_id)
                        if transcript:
                            chapters = self.youtube_service.generate_chapters_from_transcript(
                                transcript, 
                                video_info.get('duration', 0)
                            )
                    
                    # Use video title as topic if not provided
                    if not topic or topic.strip() == '':
                        topic = video_info.get('title', 'YouTube Course')
                else:
                    # Fallback if video info can't be fetched
                    topic = topic or "YouTube Course"
            else:
                topic = topic or "YouTube Course"
        else:
            topic = topic or "General Course"
        
        # Generate course structure
        course_structure = self.ai_service.generate_course_structure(
            topic, video_info, difficulty, chapters
        )
        
        # Create course
        course = Course.objects.create(
            title=course_structure['title'],
            description=course_structure['description'],
            youtube_source=youtube_url,
            difficulty=difficulty
        )
        
        # Create modules and lessons
        for module_data in course_structure['modules']:
            module = Module.objects.create(
                course=course,
                title=module_data['title'],
                order=module_data.get('order', 0)
            )
            
            for lesson_data in module_data['lessons']:
                # Find corresponding chapter for timestamp
                chapter_timestamp = None
                if chapters and 'title' in lesson_data:
                    for chapter in chapters:
                        if chapter['title'].lower() in lesson_data['title'].lower():
                            chapter_timestamp = chapter['timestamp']
                            break
                
                lesson = Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    youtube_video_id=video_id,
                    ai_notes=lesson_data.get('ai_notes', ''),
                    duration=lesson_data.get('duration', 0),
                    order=lesson_data.get('order', 0),
                    chapter_timestamp=chapter_timestamp  # Add timestamp for navigation
                )
                
                # Create quiz for the lesson
                quiz_questions = lesson_data.get('quiz_questions', [])
                if quiz_questions:
                    quiz = Quiz.objects.create(
                        lesson=lesson,
                        questions=quiz_questions
                    )
        
        return course 