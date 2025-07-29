import re
import requests
import openai
from django.conf import settings
from .models import Course, Module, Lesson, Quiz, StudyNote
import json
import time

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self._cache = {}  # Simple in-memory cache
    
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
    
    def extract_playlist_id(self, url):
        """Extract YouTube playlist ID from URL"""
        patterns = [
            r'(?:youtube\.com\/playlist\?list=|youtube\.com\/watch\?.*&list=)([^&\n?#]+)',
            r'youtube\.com\/playlist\?list=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_playlist_videos(self, playlist_id):
        """Get all videos from a YouTube playlist with caching"""
        cache_key = f"playlist_{playlist_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        if not self.api_key or self.api_key == 'your-youtube-api-key-here':
            # Return mock data when API key is not available
            mock_data = [
                {
                    'id': 'mock_video_1',
                    'title': 'Mock Video 1',
                    'description': 'This is a mock video. Please add your YouTube API key to get real playlist information.',
                    'position': 0,
                    'published_at': '2023-01-01T00:00:00Z',
                    'duration': 1800,
                    'channel': 'Mock Channel'
                },
                {
                    'id': 'mock_video_2',
                    'title': 'Mock Video 2',
                    'description': 'This is a mock video. Please add your YouTube API key to get real playlist information.',
                    'position': 1,
                    'published_at': '2023-01-01T00:00:00Z',
                    'duration': 1800,
                    'channel': 'Mock Channel'
                }
            ]
            self._cache[cache_key] = mock_data
            return mock_data
            
        url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            'part': 'snippet,contentDetails',
            'playlistId': playlist_id,
            'maxResults': 50,  # Maximum allowed by API
            'key': self.api_key
        }
        
        videos = []
        next_page_token = None
        
        try:
            while True:
                if next_page_token:
                    params['pageToken'] = next_page_token
                
                response = requests.get(url, params=params, timeout=10)  # Reduced timeout
                response.raise_for_status()
                data = response.json()
                
                for item in data['items']:
                    video_id = item['contentDetails']['videoId']
                    video_info = {
                        'id': video_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'position': item['snippet']['position'],
                        'published_at': item['snippet']['publishedAt']
                    }
                    
                    # Get additional video details (cached)
                    video_details = self.get_video_info(video_id)
                    if video_details:
                        video_info.update(video_details)
                    
                    videos.append(video_info)
                
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
                    
        except Exception as e:
            print(f"Error fetching playlist videos: {e}")
            # Return mock data on error
            error_data = [
                {
                    'id': 'error_video_1',
                    'title': 'Error Video 1',
                    'description': f'Could not fetch playlist videos. Error: {e}',
                    'position': 0,
                    'published_at': '2023-01-01T00:00:00Z',
                    'duration': 1800,
                    'channel': 'Unknown Channel'
                }
            ]
            self._cache[cache_key] = error_data
            return error_data
        
        self._cache[cache_key] = videos
        return videos
    
    def get_playlist_info(self, playlist_id):
        """Get playlist information from YouTube API with caching"""
        cache_key = f"playlist_info_{playlist_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        if not self.api_key or self.api_key == 'your-youtube-api-key-here':
            # Return mock data when API key is not available
            mock_data = {
                'title': f'Mock Playlist {playlist_id}',
                'description': 'This is a mock playlist. Please add your YouTube API key to get real playlist information.',
                'channel_title': 'Mock Channel',
                'published_at': '2023-01-01T00:00:00Z'
            }
            self._cache[cache_key] = mock_data
            return mock_data
            
        try:
            url = f"https://www.googleapis.com/youtube/v3/playlists"
            params = {
                'part': 'snippet',
                'id': playlist_id,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)  # Reduced timeout
            response.raise_for_status()
            
            data = response.json()
            if data.get('items'):
                playlist = data['items'][0]['snippet']
                result = {
                    'title': playlist.get('title', ''),
                    'description': playlist.get('description', ''),
                    'channel_title': playlist.get('channelTitle', ''),
                    'published_at': playlist.get('publishedAt', '')
                }
                self._cache[cache_key] = result
                return result
            return None
        except Exception as e:
            print(f"Error fetching playlist info: {e}")
            # Return mock data on error
            error_data = {
                'title': f'Error Playlist {playlist_id}',
                'description': f'Could not fetch playlist information. Error: {e}',
                'channel_title': 'Unknown Channel',
                'published_at': '2023-01-01T00:00:00Z'
            }
            self._cache[cache_key] = error_data
            return error_data
    
    def get_video_info(self, video_id):
        """Get video information from YouTube API with caching"""
        cache_key = f"video_info_{video_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        if not self.api_key or self.api_key == 'your-youtube-api-key-here':
            # Return mock data when API key is not available
            mock_data = {
                'title': f'Video {video_id}',
                'description': f'This is a mock description for video {video_id}. Please add your YouTube API key to get real video information.',
                'duration': 3600,  # 1 hour default
                'channel': 'Mock Channel'
            }
            self._cache[cache_key] = mock_data
            return mock_data
            
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,contentDetails',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)  # Reduced timeout
            response.raise_for_status()
            data = response.json()
            
            if data['items']:
                video = data['items'][0]
                result = {
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'duration': self._parse_duration(video['contentDetails']['duration']),
                    'channel': video['snippet']['channelTitle']
                }
                self._cache[cache_key] = result
                return result
        except Exception as e:
            print(f"Error fetching YouTube video info: {e}")
            # Return mock data on error
            error_data = {
                'title': f'Video {video_id}',
                'description': f'Could not fetch video information. Error: {e}',
                'duration': 3600,  # 1 hour default
                'channel': 'Unknown Channel'
            }
            self._cache[cache_key] = error_data
            return error_data
        
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
            response = requests.get(url, params=params, timeout=15)  # Add timeout
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
    
    def search_youtube_videos(self, search_term, max_results=5):
        """Search for YouTube videos using the Data API"""
        if not self.api_key:
            return []
            
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': search_term,
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance',
                'videoDuration': 'medium',  # 4-20 minutes
                'videoDefinition': 'high',  # HD videos
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for item in data.get('items', []):
                    video_info = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'channel_title': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'thumbnail': item['snippet']['thumbnails']['medium']['url']
                    }
                    videos.append(video_info)
                    
                return videos
                
        except Exception as e:
            print(f"Error searching YouTube videos: {e}")
            
        return []
    
    def extract_chapters_from_description(self, description):
        """Extract chapters from video description"""
        chapters = []
        lines = description.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for various timestamp patterns
            patterns = [
                r'(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)',  # 1:23 Chapter Title
                r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]\s*(.+)',  # 1:23 - Chapter Title
                r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[•·]\s*(.+)',  # 1:23 • Chapter Title
                r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[\(\[].+?[\)\]]\s*(.+)',  # 1:23 (Intro) Chapter Title
                r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[0-9]+\.\s*(.+)',  # 1:23 1. Chapter Title
                r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[a-zA-Z]\)\s*(.+)',  # 1:23 a) Chapter Title
                r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[A-Z]\.\s*(.+)',  # 1:23 A. Chapter Title
                r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[0-9]+\)\s*(.+)',  # 1:23 1) Chapter Title
            ]
            
            for pattern in patterns:
                timestamp_match = re.search(pattern, line)
                if timestamp_match:
                    timestamp = timestamp_match.group(1)
                    title = timestamp_match.group(2).strip()
                    # Clean up title
                    title = re.sub(r'^[-–—•·\s]+', '', title)  # Remove leading symbols
                    title = re.sub(r'[-–—•·\s]+$', '', title)  # Remove trailing symbols
                    title = re.sub(r'^[0-9]+\.\s*', '', title)  # Remove leading numbers
                    title = re.sub(r'^[a-zA-Z]\)\s*', '', title)  # Remove leading letters
                    title = re.sub(r'^[A-Z]\.\s*', '', title)  # Remove leading capital letters
                    title = re.sub(r'^[0-9]+\)\s*', '', title)  # Remove leading numbers with )
                    
                    if title and len(title) > 3:
                        seconds = self._timestamp_to_seconds(timestamp)
                        chapters.append({
                            'timestamp': timestamp,
                            'title': title,
                            'seconds': seconds
                        })
                    break
        
        # Sort chapters by timestamp
        chapters.sort(key=lambda x: x['seconds'])
        return chapters
    
    def generate_chapters_from_transcript(self, transcript, video_duration):
        """Generate chapters from transcript using AI"""
        if not transcript or not settings.OPENAI_API_KEY:
            return []
        
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            prompt = f"""
            Analyze this video transcript and create detailed, meaningful chapters with timestamps.
            Video duration: {video_duration} seconds
            
            Transcript:
            {transcript[:3000]}...
            
            Create 8-12 detailed chapters that cover:
            1. Introduction and overview
            2. Key concepts and main topics
            3. Practical examples and demonstrations
            4. Important tips and best practices
            5. Common mistakes and how to avoid them
            6. Advanced techniques and tips
            7. Summary and next steps
            
            Each chapter should be meaningful and cover a specific topic or concept.
            Distribute chapters evenly throughout the video duration.
            
            Return chapters in this exact format:
            - 00:00 Introduction and Overview
            - 02:30 Key Concepts Explained
            - 05:15 Practical Examples
            - 08:45 Best Practices
            - 12:20 Common Mistakes
            - 15:30 Advanced Techniques
            - 18:45 Tips and Tricks
            - 22:10 Summary and Conclusion
            
            Make sure timestamps are realistic and evenly distributed across the video duration.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
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
        self._cache = {}  # Simple in-memory cache for AI responses
    
    def generate_course_structure(self, topic, video_info=None, difficulty='beginner', chapters=None):
        """Generate course structure with AI notes included - optimized for speed"""
        cache_key = f"course_structure_{topic}_{difficulty}_{hash(str(chapters))}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        if not self.client:
            result = self._generate_mock_structure(topic, difficulty, chapters)
            self._cache[cache_key] = result
            return result
            
        # Simplified prompt for faster response
        prompt_parts = [
            f"Generate a concise course structure for '{topic}' at {difficulty} level."
        ]
        
        if video_info:
            prompt_parts.append(f"Based on: {video_info.get('title', 'Unknown')}")
        
        if chapters:
            prompt_parts.append("Use these chapters:")
            for chapter in chapters[:6]:  # Reduced from 8 to 6
                prompt_parts.append(f"- {chapter['timestamp']}: {chapter['title']}")
        
        prompt = "\n".join(prompt_parts) + """
        
        Generate a course structure with:
        1. Course title and description
        2. 2-3 modules, each with 2-3 lessons (reduced for speed)
        3. Each lesson should have a title and brief description
        4. Include 2-3 quiz questions per lesson
        
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
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,  # Reduced for consistency
                max_tokens=800,  # Further reduced for speed
                timeout=15  # Reduced timeout
            )
            
            result = json.loads(response.choices[0].message.content)
            self._cache[cache_key] = result
            return result
        except Exception as e:
            print(f"Error generating course structure: {e}")
            result = self._generate_mock_structure(topic, difficulty, chapters)
            self._cache[cache_key] = result
            return result
    
    def generate_comprehensive_course_structure(self, prompt, difficulty='beginner'):
        """Generate comprehensive course structure from learning prompt with YouTube content curation"""
        cache_key = f"comprehensive_course_{prompt}_{difficulty}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        if not self.client:
            result = self._generate_mock_comprehensive_structure(prompt, difficulty)
            self._cache[cache_key] = result
            return result
            
        # Comprehensive prompt for detailed course generation
        prompt_text = f"""
        Create a comprehensive learning course for: "{prompt}"
        Difficulty Level: {difficulty}
        
        Follow this detailed process:
        
        1. TOPIC ANALYSIS:
        - Parse the learning intent and identify core subject matter
        - Extract skill level indicators and specific learning goals
        - Identify prerequisite concepts and logical learning progression
        
        2. KNOWLEDGE MAPPING:
        - Break down the main topic into prerequisite concepts
        - Map concept dependencies (what must be learned before what)
        - Design appropriate skill milestones and checkpoints
        
        3. CONTENT STRATEGY:
        - Plan optimal learning sequence based on concept difficulty
        - Identify potential knowledge gaps that need filling
        - Design assessment points and practical applications
        
        4. COURSE STRUCTURE:
        - Group related concepts into logical modules (4-6 modules)
        - Ensure each module has clear learning objectives
        - Balance module length and complexity
        - Create smooth transitions between modules
        
        5. LESSON PLANNING:
        - Break modules into digestible lesson chunks (3-5 lessons per module)
        - Sequence lessons for optimal knowledge building
        - Plan mix of theory, examples, and practical application
        - Design appropriate pacing for {difficulty} level
        
        6. YOUTUBE CONTENT CURATION:
        - For each lesson, provide specific YouTube search terms to find relevant videos
        - Focus on high-quality educational content from reputable channels
        - Include both theoretical and practical content
        - Suggest search terms that will find videos with good explanations
        
        7. ASSESSMENT INTEGRATION:
        - Plan quiz placement for optimal retention
        - Design varied question types per topic
        - Create progressive difficulty in assessments
        - Plan final projects or practical applications
        
        Format as JSON:
        {{
            "title": "Comprehensive Course Title",
            "description": "Detailed course description",
            "modules": [
                {{
                    "title": "Module Title",
                    "description": "Module description",
                    "lessons": [
                        {{
                            "title": "Lesson Title",
                            "description": "Lesson description",
                            "type": "video",
                            "duration": 1800,
                            "youtube_search_term": "specific search term for this lesson",
                            "chapter_timestamp": "00:00",
                            "video_info": {{
                                "title": "Expected video title",
                                "description": "Expected video description"
                            }}
                        }}
                    ]
                }}
            ]
        }}
        
        For YouTube search terms, use specific, targeted terms that will find high-quality educational videos.
        Examples: "python for beginners tutorial", "machine learning basics explained", "data science fundamentals"
        
        Ensure the course is comprehensive, well-structured, and suitable for {difficulty} level learners.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.7,
                max_tokens=2000,
                timeout=30
            )
            
            result = json.loads(response.choices[0].message.content)
            self._cache[cache_key] = result
            return result
        except Exception as e:
            print(f"Error generating comprehensive course structure: {e}")
            result = self._generate_mock_comprehensive_structure(prompt, difficulty)
            self._cache[cache_key] = result
            return result
    
    def generate_structured_study_notes(self, lesson_title, video_info=None, chapter_info=None):
        """Generate 3 types of study notes: Golden Notes, Summaries, and Own Notes"""
        cache_key = f"enhanced_study_notes_{lesson_title}_{hash(str(video_info))}_{hash(str(chapter_info))}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        if not self.client:
            mock_notes = self._generate_mock_enhanced_notes(lesson_title)
            self._cache[cache_key] = mock_notes
            return mock_notes
        
        # Get video transcript for dynamic content
        transcript = ""
        if video_info and video_info.get('id'):
            transcript = self._get_video_transcript(video_info['id'])
        
        # Create context for the notes
        context = f"Module: {lesson_title}"
        if video_info:
            context += f"\nVideo: {video_info.get('title', '')}"
            if video_info.get('description'):
                context += f"\nDescription: {video_info['description'][:500]}..."
        
        # If this is a module with multiple lessons, include lesson information
        if chapter_info and chapter_info.get('lessons'):
            context += f"\n\nThis module contains the following lessons:"
            for i, lesson in enumerate(chapter_info['lessons'], 1):
                context += f"\n{i}. {lesson.get('title', 'Unknown lesson')}"
                if lesson.get('chapter_timestamp'):
                    context += f" (starts at {lesson['chapter_timestamp']})"
        
        # Add transcript to context for dynamic generation
        if transcript:
            context += f"\n\nVideo Transcript:\n{transcript[:2000]}..."  # Limit transcript length
        
        # Generate Golden Notes (Deep, comprehensive explanations)
        golden_notes_prompt = f"""
        {context}
        
        Generate GOLDEN NOTES for this lesson based on the actual video content and transcript provided. These should be deep, comprehensive explanations that expand beyond the video content with additional context and examples.
        
        Create 5-8 concept cards in this JSON format based on the actual video content:
        [
            {{
                "title": "Concept Title (based on actual video content)",
                "explanation": "A comprehensive definition and explanation that goes beyond basic understanding. Include academic context, real-world applications, and deeper insights. Make it educational and thorough based on the video content.",
                "examples": ["Specific real-world example 1", "Industry application 2", "Case study 3"],
                "key_points": ["Critical insight 1", "Important detail 2", "Key understanding 3"]
            }}
        ]
        
        Focus on the actual concepts, topics, and themes discussed in the video. Make each concept card comprehensive and educational, providing deep insights that go beyond basic understanding. Use formal, academic language similar to university-level content.
        """
        
        # Generate Summaries (Quick, scannable bullet points)
        summaries_prompt = f"""
        {context}
        
        Generate SUMMARIES for this lesson based on the actual video content and transcript provided. These should be quick, scannable bullet points of key concepts (1-2 sentences each).
        
        Create 8-12 summary points in this JSON format based on the actual video content:
        [
            "Concise definition and explanation of key concept 1 from the video",
            "Quick summary of important theory or practice 2 from the video", 
            "Brief explanation of critical business concept 3 from the video"
        ]
        
        Make each summary point concise, clear, and easy to scan for quick review. Focus on the actual content discussed in the video with formal language.
        """
        
        try:
            # Generate Golden Notes
            golden_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": golden_notes_prompt}],
                temperature=0.3,
                max_tokens=1000,
                timeout=20
            )
            
            # Generate Summaries
            summaries_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": summaries_prompt}],
                temperature=0.3,
                max_tokens=600,
                timeout=15
            )
            
            # Parse responses
            golden_notes_content = golden_response.choices[0].message.content.strip()
            summaries_content = summaries_response.choices[0].message.content.strip()
            
            # Parse JSON responses
            golden_notes = self._parse_json_response(golden_notes_content)
            summaries = self._parse_json_response(summaries_content)
            
            # Create enhanced notes structure
            enhanced_notes = {
                'golden_notes': golden_notes,
                'summaries': summaries,
                'own_notes': "",  # Empty for user to fill
                'content': f"# 📝 {lesson_title} - Enhanced Study Guide\n\n## Golden Notes\n{self._format_golden_notes(golden_notes)}\n\n## Summaries\n{self._format_summaries(summaries)}",
                'key_concepts': [card['title'] for card in golden_notes],
                'code_examples': [],
                'summary': f"Enhanced study guide for {lesson_title} with comprehensive golden notes and quick summaries."
            }
            
            self._cache[cache_key] = enhanced_notes
            return enhanced_notes
            
        except Exception as e:
            print(f"Error generating enhanced study notes: {e}")
            mock_notes = self._generate_mock_enhanced_notes(lesson_title)
            self._cache[cache_key] = mock_notes
            return mock_notes
    
    def _parse_json_response(self, content):
        """Parse JSON response from AI, with fallback to structured parsing"""
        try:
            # Try to extract JSON from the response
            import json
            # Find JSON array in the content
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: return empty array
        return []
    
    def _format_golden_notes(self, golden_notes):
        """Format golden notes for markdown display"""
        if not golden_notes:
            return "No golden notes available."
        
        formatted = ""
        for i, card in enumerate(golden_notes, 1):
            formatted += f"\n### {i}. {card.get('title', 'Concept')}\n"
            formatted += f"{card.get('explanation', 'No explanation available.')}\n"
            
            if card.get('examples'):
                formatted += "\n**Examples:**\n"
                for example in card['examples']:
                    formatted += f"- {example}\n"
            
            if card.get('key_points'):
                formatted += "\n**Key Points:**\n"
                for point in card['key_points']:
                    formatted += f"- {point}\n"
            formatted += "\n"
        
        return formatted
    
    def _format_summaries(self, summaries):
        """Format summaries for markdown display"""
        if not summaries:
            return "No summaries available."
        
        formatted = ""
        for i, summary in enumerate(summaries, 1):
            formatted += f"{i}. {summary}\n"
        
        return formatted
    
    def _generate_mock_study_notes(self, lesson_title):
        """Generate mock study notes when AI is not available"""
        content = f"""# 📝 {lesson_title} - Complete Study Guide

## 🎯 Key Concepts
- Understanding the fundamentals of {lesson_title.lower()}
- Key principles and best practices
- Important concepts to remember
- Advanced techniques and applications
- Common patterns and solutions

## 💻 Code Examples
```python
# Example code for {lesson_title.lower()}
def example_function():
    return "This is an example"

# Advanced implementation
class AdvancedExample:
    def __init__(self):
        self.data = []
    
    def process_data(self):
        return "Processed data"
```

## 📋 Quick Summary
This module covers the essential concepts of {lesson_title.lower()}. Understanding these fundamentals is crucial for building a strong foundation. The lessons provide comprehensive coverage of key topics, practical examples, and real-world applications."""
        
        return {
            'content': content,
            'key_concepts': [
                f"Understanding the fundamentals of {lesson_title.lower()}",
                "Key principles and best practices",
                "Important concepts to remember",
                "Advanced techniques and applications",
                "Common patterns and solutions"
            ],
            'code_examples': [
                f"# Example code for {lesson_title.lower()}\ndef example_function():\n    return \"This is an example\"",
                f"# Advanced implementation\nclass AdvancedExample:\n    def __init__(self):\n        self.data = []\n    \n    def process_data(self):\n        return \"Processed data\""
            ],
            'summary': f"This module covers the essential concepts of {lesson_title.lower()}. Understanding these fundamentals is crucial for building a strong foundation. The lessons provide comprehensive coverage of key topics, practical examples, and real-world applications."
        }
    
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
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=800,  # Reduced for faster response
                timeout=20  # Add timeout
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

    def _generate_mock_enhanced_notes(self, lesson_title):
        """Generate mock enhanced notes with 3 types: Golden Notes, Summaries, and Own Notes"""
        golden_notes = [
            {
                "title": "Bureaucracy",
                "explanation": "An organizational form characterized by hierarchical structures and formalized rules that guide impersonal and rational decision-making. This management approach emphasizes efficiency through standardized procedures and clear authority chains.",
                "examples": ["Government agencies and departments", "Large corporations with formal hierarchies", "Educational institutions with administrative structures"],
                "key_points": ["Emphasizes efficiency through standardization", "Uses formal rules and procedures", "Creates clear authority hierarchies"]
            },
            {
                "title": "Corporate Social Responsibility",
                "explanation": "Business practices emphasizing the importance of ethical and sustainable conduct towards the environment and society. Organizations integrate social and environmental concerns into their business operations and stakeholder interactions.",
                "examples": ["Environmental sustainability initiatives", "Community development programs", "Ethical supply chain management"],
                "key_points": ["Balances profit with social impact", "Addresses stakeholder concerns", "Promotes sustainable business practices"]
            },
            {
                "title": "Globalization",
                "explanation": "The increasing interconnectedness of economies and societies due to advances in information and communication technologies. This process facilitates cross-border trade, cultural exchange, and international collaboration.",
                "examples": ["Multinational corporations expanding globally", "International trade agreements and partnerships", "Cross-cultural business practices"],
                "key_points": ["Enables international market access", "Promotes cultural exchange", "Creates competitive advantages"]
            },
            {
                "title": "Narrative",
                "explanation": "The structured account of events or stories used in organizations to convey meaning, values, and goals to employees. Effective narratives help align organizational culture and guide decision-making processes.",
                "examples": ["Company origin stories and mission statements", "Brand narratives and marketing campaigns", "Organizational change communication"],
                "key_points": ["Conveys organizational values and culture", "Guides decision-making processes", "Builds employee engagement and alignment"]
            },
            {
                "title": "Scientific Management",
                "explanation": "A management theory focusing on optimizing labor productivity by scientifically studying workflows and systematically training employees. This approach emphasizes efficiency through systematic analysis and standardization.",
                "examples": ["Assembly line production methods", "Time and motion studies", "Standardized training programs"],
                "key_points": ["Optimizes workflow efficiency", "Uses systematic analysis", "Standardizes work processes"]
            },
            {
                "title": "Competitive Advantage",
                "explanation": "The attributes or strategies that allow an organization to outperform its rivals by offering unique value propositions. This includes distinctive capabilities, resources, or market positioning that create sustainable competitive barriers.",
                "examples": ["Proprietary technology and intellectual property", "Strong brand recognition and customer loyalty", "Operational excellence and cost leadership"],
                "key_points": ["Creates sustainable market position", "Differentiates from competitors", "Delivers unique customer value"]
            }
        ]
        
        summaries = [
            "Bureaucracy emphasizes hierarchical structures and formalized rules for efficient decision-making",
            "Corporate Social Responsibility balances profit with ethical and sustainable business practices",
            "Globalization increases economic and cultural interconnectedness through technology advances",
            "Narrative structures help organizations convey meaning, values, and goals to stakeholders",
            "Scientific Management optimizes productivity through systematic workflow analysis and standardization",
            "Competitive Advantage enables organizations to outperform rivals through unique value propositions",
            "Organizational culture shapes employee behavior and decision-making processes",
            "Stakeholder management balances diverse interests and expectations effectively"
        ]
        
        return {
            'golden_notes': golden_notes,
            'summaries': summaries,
            'own_notes': "",
            'content': f"# 📝 {lesson_title} - Enhanced Study Guide\n\n## Golden Notes\n{self._format_golden_notes(golden_notes)}\n\n## Summaries\n{self._format_summaries(summaries)}",
            'key_concepts': [card['title'] for card in golden_notes],
            'code_examples': [],
            'summary': f"Enhanced study guide for {lesson_title} with comprehensive golden notes and quick summaries."
        }

    def _generate_mock_comprehensive_structure(self, prompt, difficulty):
        """Generate mock comprehensive course structure for prompt-based generation"""
        return {
            "title": f"Comprehensive {prompt} Course",
            "description": f"AI-generated comprehensive course on {prompt} for {difficulty} level learners",
            "modules": [
                {
                    "title": "Introduction to the Topic",
                    "description": "Foundation concepts and overview",
                    "lessons": [
                        {
                            "title": "Getting Started",
                            "description": "Introduction to the subject matter",
                            "type": "video",
                            "duration": 1800,
                            "youtube_search_term": f"{prompt} for beginners tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Introduction Video",
                                "description": "Basic introduction to the topic"
                            }
                        },
                        {
                            "title": "Core Concepts",
                            "description": "Understanding fundamental principles",
                            "type": "video",
                            "duration": 2400,
                            "youtube_search_term": f"{prompt} fundamentals explained",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Core Concepts Video",
                                "description": "Deep dive into core concepts"
                            }
                        }
                    ]
                },
                {
                    "title": "Intermediate Topics",
                    "description": "Building on foundational knowledge",
                    "lessons": [
                        {
                            "title": "Advanced Techniques",
                            "description": "Moving beyond basics",
                            "type": "video",
                            "duration": 2100,
                            "youtube_search_term": f"{prompt} advanced techniques tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Advanced Techniques Video",
                                "description": "Advanced methods and techniques"
                            }
                        },
                        {
                            "title": "Practical Applications",
                            "description": "Real-world implementation",
                            "type": "video",
                            "duration": 2700,
                            "youtube_search_term": f"{prompt} practical examples tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Practical Applications Video",
                                "description": "Hands-on practical examples"
                            }
                        }
                    ]
                },
                {
                    "title": "Advanced Topics",
                    "description": "Mastery level content",
                    "lessons": [
                        {
                            "title": "Expert Techniques",
                            "description": "Professional-level skills",
                            "type": "video",
                            "duration": 3000,
                            "youtube_search_term": f"{prompt} expert level tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Expert Techniques Video",
                                "description": "Expert-level techniques and strategies"
                            }
                        },
                        {
                            "title": "Final Project",
                            "description": "Comprehensive project to demonstrate mastery",
                            "type": "video",
                            "duration": 3600,
                            "youtube_search_term": f"{prompt} complete project tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Final Project Video",
                                "description": "Complete project walkthrough"
                            }
                        }
                    ]
                }
            ]
        }

    def _get_video_transcript(self, video_id):
        """Get video transcript for dynamic content generation"""
        try:
            from .services import YouTubeService
            yt_service = YouTubeService()
            transcript = yt_service.get_video_transcript(video_id)
            return transcript if transcript else ""
        except Exception as e:
            print(f"Error getting transcript for video {video_id}: {e}")
            return ""

class CourseGenerationService:
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.ai_service = AIService()
    
    def generate_course(self, youtube_url=None, topic=None, difficulty='beginner', prompt=None, generation_type=None):
        """Generate a course from YouTube URL, topic, or learning prompt"""
        if not youtube_url and not topic and not prompt:
            raise ValueError("Either youtube_url, topic, or prompt must be provided")
        
        # Handle prompt-based generation
        if generation_type == 'prompt' and prompt:
            return self._generate_prompt_course(prompt, difficulty)
        
        # Handle link-based generation
        if youtube_url:
            # Check if it's a playlist
            playlist_id = self.youtube_service.extract_playlist_id(youtube_url)
            video_id = self.youtube_service.extract_video_id(youtube_url)
            
            if playlist_id:
                return self._generate_playlist_course(playlist_id, topic, difficulty)
            elif video_id:
                return self._generate_single_video_course(video_id, topic, difficulty)
            else:
                return self._generate_topic_course(topic, difficulty)
        else:
            return self._generate_topic_course(topic, difficulty)
    
    def _generate_playlist_course(self, playlist_id, topic, difficulty):
        """Generate course from YouTube playlist"""
        playlist_info = self.youtube_service.get_playlist_info(playlist_id)
        
        if not playlist_info:
            raise ValueError("Could not fetch playlist information")
        
        # Get all videos in the playlist
        playlist_videos = self.youtube_service.get_playlist_videos(playlist_id)
        
        if not playlist_videos:
            raise ValueError("Could not fetch playlist videos")
        
        # Use playlist title as topic if not provided
        if not topic or topic.strip() == '':
            topic = playlist_info.get('title', 'Playlist Course')
        
        # Create course
        course = Course.objects.create(
            title=playlist_info.get('title', topic),
            description=playlist_info.get('description', '')[:500] + '...' if playlist_info.get('description') else f'Course based on {topic} playlist',
            youtube_source=f"https://www.youtube.com/playlist?list={playlist_id}",
            playlist_url=f"https://www.youtube.com/playlist?list={playlist_id}",
            difficulty=difficulty,
            generation_type='link'
        )
        
        module_order = 0
        
        for video_data in playlist_videos:
            video_id = video_data['id']  # Changed from 'video_id' to 'id'
            video_title = video_data['title']
            
            # Get video info and chapters
            video_info = self.youtube_service.get_video_info(video_id)
            chapters = []
            
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
            
            # Create module for this video
            if chapters:
                # Structure chapters into modules for this video
                video_modules = self._structure_chapters_with_study_notes(chapters, video_id, video_info)
                
                for module_data in video_modules:
                    module = Module.objects.create(
                        course=course,
                        title=f"{video_title} - {module_data['title']}",
                        order=module_order,
                        video_id=video_id
                    )
                    
                    lesson_order = 0
                    for lesson_data in module_data['lessons']:
                        # Create video lesson
                        video_lesson = Lesson.objects.create(
                            module=module,
                            title=lesson_data['title'],
                            lesson_type='video',
                            youtube_video_id=video_id,
                            duration=lesson_data.get('duration', 0),
                            order=lesson_order,
                            chapter_timestamp=lesson_data.get('chapter_timestamp', '')
                        )
                        lesson_order += 1
                    
                    # Create ONE study notes lesson per module (combining all lessons)
                    module_title = module_data['title'].replace('Module ', '').replace(':', '')
                    study_notes = self.ai_service.generate_structured_study_notes(
                        f"Complete {module_title} Study Guide", 
                        video_info, 
                        {'title': module_title, 'lessons': module_data['lessons']}
                    )
                    
                    notes_lesson = Lesson.objects.create(
                        module=module,
                        title=f"📝 Complete Study Notes - {module_title}",
                        lesson_type='notes',
                        order=lesson_order
                    )
                    
                    # Create StudyNote object
                    StudyNote.objects.create(
                        lesson=notes_lesson,
                        golden_notes=study_notes['golden_notes'],
                        summaries=study_notes['summaries'],
                        own_notes=study_notes['own_notes'],
                        content=study_notes['content'],
                        key_concepts=study_notes['key_concepts'],
                        code_examples=study_notes['code_examples'],
                        summary=study_notes['summary']
                    )
                    
                    module_order += 1
            else:
                # No chapters found, create a single module for this video
                module = Module.objects.create(
                    course=course,
                    title=f"Video: {video_title}",
                    order=module_order,
                    video_id=video_id
                )
                
                # Create video lesson
                video_lesson = Lesson.objects.create(
                    module=module,
                    title=video_title,
                    lesson_type='video',
                    youtube_video_id=video_id,
                    duration=video_info.get('duration', 0) if video_info else 0,
                    order=0
                )
                
                # Create study notes lesson
                study_notes = self.ai_service.generate_structured_study_notes(
                    video_title, 
                    video_info
                )
                
                notes_lesson = Lesson.objects.create(
                    module=module,
                    title=f"📝 Study Notes - {video_title}",
                    lesson_type='notes',
                    order=1
                )
                
                # Create StudyNote object
                StudyNote.objects.create(
                    lesson=notes_lesson,
                    golden_notes=study_notes['golden_notes'],
                    summaries=study_notes['summaries'],
                    own_notes=study_notes['own_notes'],
                    content=study_notes['content'],
                    key_concepts=study_notes['key_concepts'],
                    code_examples=study_notes['code_examples'],
                    summary=study_notes['summary']
                )
                
                module_order += 1
        
        return course
    
    def _generate_video_notes(self, video_title, video_description):
        """Generate AI notes for an entire video"""
        if not self.ai_service.client:
            return f"AI-generated notes for {video_title}. This video covers important concepts and provides valuable insights."
        
        try:
            prompt = f"""
            Create comprehensive study notes for this video: "{video_title}"
            
            Video description: {video_description[:500]}...
            
            Generate detailed notes that include:
            - Key concepts and main points
            - Important definitions and explanations
            - Practical examples and applications
            - Summary of key takeaways
            
            Format the notes in a clear, structured way that's easy to follow.
            """
            
            response = self.ai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating video notes: {e}")
            return f"AI-generated notes for {video_title}. This video covers important concepts and provides valuable insights."
    
    def _generate_chapter_notes(self, chapter_title, video_title, video_description, timestamp):
        """Generate AI notes for a specific chapter"""
        if not self.ai_service.client:
            return f"AI-generated notes for {chapter_title} from {video_title}. This chapter covers important concepts and provides valuable insights."
        
        try:
            prompt = f"""
            Create detailed study notes for this specific chapter: "{chapter_title}"
            From video: "{video_title}"
            Chapter starts at: {timestamp}
            
            Video description: {video_description[:500]}...
            
            Generate focused notes for this chapter that include:
            - Key concepts covered in this specific section
            - Important points and explanations
            - Examples and practical applications
            - Summary of what was learned in this chapter
            
            Format the notes in a clear, structured way that's easy to follow.
            """
            
            response = self.ai_service.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating chapter notes: {e}")
            return f"AI-generated notes for {chapter_title} from {video_title}. This chapter covers important concepts and provides valuable insights."
    
    def _generate_single_video_course(self, video_id, topic, difficulty):
        """Generate course from single YouTube video with optimized structure"""
        video_info = self.youtube_service.get_video_info(video_id)
        
        if not video_info:
            raise ValueError("Could not fetch video information")
        
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
        
        # Create course
        course = Course.objects.create(
            title=video_info.get('title', topic),
            description=video_info.get('description', '')[:500] + '...' if video_info.get('description') else f'Course based on {topic}',
            youtube_source=f"https://www.youtube.com/watch?v={video_id}",
            difficulty=difficulty,
            generation_type='link'
        )
        
        if chapters:
            # Structure chapters into modules with study notes
            modules = self._structure_chapters_with_study_notes(chapters, video_id, video_info)
            
            # Create modules and lessons
            for module_data in modules:
                module = Module.objects.create(
                    course=course,
                    title=module_data['title'],
                    order=module_data['order']
                )
                
                lesson_order = 0
                for lesson_data in module_data['lessons']:
                    # Create video lesson
                    video_lesson = Lesson.objects.create(
                        module=module,
                        title=lesson_data['title'],
                        lesson_type='video',
                        youtube_video_id=video_id,
                        duration=lesson_data.get('duration', 0),
                        order=lesson_order,
                        chapter_timestamp=lesson_data.get('chapter_timestamp', '')
                    )
                    lesson_order += 1
                
                # Create ONE study notes lesson per module (combining all lessons)
                module_title = module_data['title'].replace('Module ', '').replace(':', '')
                study_notes = self.ai_service.generate_structured_study_notes(
                    f"Complete {module_title} Study Guide", 
                    video_info, 
                    {'title': module_title, 'lessons': module_data['lessons']}
                )
                
                notes_lesson = Lesson.objects.create(
                    module=module,
                    title=f"📝 Complete Study Notes - {module_title}",
                    lesson_type='notes',
                    order=lesson_order
                )
                
                # Create StudyNote object
                StudyNote.objects.create(
                    lesson=notes_lesson,
                    golden_notes=study_notes['golden_notes'],
                    summaries=study_notes['summaries'],
                    own_notes=study_notes['own_notes'],
                    content=study_notes['content'],
                    key_concepts=study_notes['key_concepts'],
                    code_examples=study_notes['code_examples'],
                    summary=study_notes['summary']
                )
        else:
            # No chapters found, generate AI course structure
            course_structure = self.ai_service.generate_course_structure(
                topic, video_info, difficulty, chapters
            )
            
            # Update course with AI-generated title and description
            course.title = course_structure['title']
            course.description = course_structure['description']
            course.save()
            
            # Create modules and lessons
            for module_data in course_structure['modules']:
                module = Module.objects.create(
                    course=course,
                    title=module_data['title'],
                    order=module_data.get('order', 0)
                )
                
                lesson_order = 0
                for lesson_data in module_data['lessons']:
                    # Create video lesson
                    video_lesson = Lesson.objects.create(
                        module=module,
                        title=lesson_data['title'],
                        lesson_type='video',
                        youtube_video_id=video_id,
                        duration=lesson_data.get('duration', 0),
                        order=lesson_order
                    )
                    lesson_order += 1
                
                # Create ONE study notes lesson per module
                study_notes = self.ai_service.generate_structured_study_notes(
                    f"Complete {module_data['title']} Study Guide", 
                    video_info
                )
                
                notes_lesson = Lesson.objects.create(
                    module=module,
                    title=f"📝 Complete Study Notes - {module_data['title']}",
                    lesson_type='notes',
                    order=lesson_order
                )
                
                # Create StudyNote object
                StudyNote.objects.create(
                    lesson=notes_lesson,
                    golden_notes=study_notes['golden_notes'],
                    summaries=study_notes['summaries'],
                    own_notes=study_notes['own_notes'],
                    content=study_notes['content'],
                    key_concepts=study_notes['key_concepts'],
                    code_examples=study_notes['code_examples'],
                    summary=study_notes['summary']
                )
                
                # Create quiz if questions provided
                quiz_questions = lesson_data.get('quiz_questions', [])
                if quiz_questions:
                    quiz_lesson = Lesson.objects.create(
                        module=module,
                        title=f"Quiz - {module_data['title']}",
                        lesson_type='quiz',
                        order=lesson_order + 1
                    )
                    
                    quiz = Quiz.objects.create(
                        lesson=quiz_lesson,
                        questions=quiz_questions
                    )
        
        return course

    def _structure_chapters_with_study_notes(self, chapters, video_id, video_info):
        """Structure chapters into modules with study notes - optimized version"""
        modules = []
        current_module = {
            'title': '',
            'order': 0,
            'lessons': [],
            'total_duration': 0
        }
        
        for i, chapter in enumerate(chapters):
            duration = chapter.get('seconds', 0)
            title = chapter['title']
            
            # Simplified module structure for faster generation
            if len(current_module['lessons']) >= 3:  # Max 3 lessons per module
                # Finalize current module
                if current_module['lessons']:
                    modules.append(current_module)
                
                # Start new module
                current_module = {
                    'title': f"Module {len(modules) + 1}: {title}",
                    'order': len(modules),
                    'lessons': [],
                    'total_duration': 0
                }
            
            # Add lesson to current module (no AI notes generation here - will be done later)
            current_module['lessons'].append({
                'title': title,
                'youtube_video_id': video_id,
                'duration': duration,
                'order': len(current_module['lessons']),
                'chapter_timestamp': chapter['timestamp']
            })
            current_module['total_duration'] += duration
        
        # Add the last module if it has lessons
        if current_module['lessons']:
            modules.append(current_module)
        
        return modules
    
    def _structure_chapters_into_modules(self, chapters, video_id, video_info):
        """Structure chapters into modules based on duration and type"""
        modules = []
        current_module = {
            'title': '',
            'order': 0,
            'lessons': [],
            'total_duration': 0
        }
        
        for i, chapter in enumerate(chapters):
            duration = chapter.get('seconds', 0)
            title = chapter['title']
            
            # Determine module type based on duration
            if duration <= 600:  # 10 minutes or less
                module_type = "Micro Module"
                max_duration = 600
            elif duration <= 1200:  # 10-20 minutes
                module_type = "Standard Module"
                max_duration = 1200
            elif duration <= 2400:  # 20-40 minutes
                module_type = "Deep Dive Module"
                max_duration = 2400
            else:  # > 40 minutes
                module_type = "Max Module"
                max_duration = 3600  # 1 hour max
            
            # Check if we need to start a new module
            if (current_module['total_duration'] + duration > max_duration and 
                len(current_module['lessons']) > 0):
                
                # Finalize current module
                if current_module['lessons']:
                    modules.append(current_module)
                
                # Start new module
                current_module = {
                    'title': f"{module_type}: {title}",
                    'order': len(modules),
                    'lessons': [],
                    'total_duration': 0
                }
            
            # Generate AI notes for this chapter
            chapter_notes = self._generate_chapter_notes(
                title, 
                video_info.get('title', ''), 
                video_info.get('description', ''),
                chapter['timestamp']
            )
            
            # Add lesson to current module
            current_module['lessons'].append({
                'title': title,
                'youtube_video_id': video_id,
                'ai_notes': chapter_notes,
                'duration': duration,
                'order': len(current_module['lessons']),
                'chapter_timestamp': chapter['timestamp']
            })
            current_module['total_duration'] += duration
        
        # Add the last module if it has lessons
        if current_module['lessons']:
            modules.append(current_module)
        
        return modules
    
    def _generate_mock_course(self, youtube_url, topic, difficulty):
        """Generate a mock course for testing"""
        # Extract video ID for mock data
        video_id = self.youtube_service.extract_video_id(youtube_url) if youtube_url else 'mock_video_123'
        
        # Create course
        course = Course.objects.create(
            title=f"{topic or 'Python'} Course - Mock Data",
            description=f"Mock course for testing. Video: {video_id}",
            youtube_source=youtube_url or "https://www.youtube.com/watch?v=mock",
            difficulty=difficulty,
            generation_type='link'
        )
        
        # Create mock modules
        modules_data = [
            {
                'title': 'Introduction',
                'lessons': [
                    {'title': 'Getting Started', 'duration': 300, 'ai_notes': 'Mock notes for getting started'},
                    {'title': 'Basic Concepts', 'duration': 600, 'ai_notes': 'Mock notes for basic concepts'},
                ]
            },
            {
                'title': 'Core Topics',
                'lessons': [
                    {'title': 'Main Topic 1', 'duration': 450, 'ai_notes': 'Mock notes for topic 1'},
                    {'title': 'Main Topic 2', 'duration': 450, 'ai_notes': 'Mock notes for topic 2'},
                ]
            },
            {
                'title': 'Advanced Topics',
                'lessons': [
                    {'title': 'Advanced Concept 1', 'duration': 600, 'ai_notes': 'Mock notes for advanced topic 1'},
                    {'title': 'Advanced Concept 2', 'duration': 600, 'ai_notes': 'Mock notes for advanced topic 2'},
                ]
            }
        ]
        
        # Create modules and lessons
        for i, module_data in enumerate(modules_data):
            module = Module.objects.create(
                course=course,
                title=module_data['title'],
                order=i,
                video_id=video_id
            )
            
            for j, lesson_data in enumerate(module_data['lessons']):
                lesson = Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    ai_notes=lesson_data['ai_notes'],
                    duration=lesson_data['duration'],
                    order=j,
                    youtube_video_id=video_id,
                    chapter_timestamp=f"{j*5:02d}:00"
                )
        
        return course

    def _generate_topic_course(self, topic, difficulty):
        """Generate course from topic only (no video)"""
        course_structure = self.ai_service.generate_course_structure(topic, None, difficulty)
        
        course = Course.objects.create(
            title=course_structure['title'],
            description=course_structure['description'],
            difficulty=difficulty,
            generation_type='topic'
        )
        
        for module_data in course_structure['modules']:
            module = Module.objects.create(
                course=course,
                title=module_data['title'],
                order=module_data.get('order', 0)
            )
            
            for lesson_data in module_data['lessons']:
                lesson = Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    ai_notes=lesson_data.get('ai_notes', ''),
                    duration=lesson_data.get('duration', 0),
                    order=lesson_data.get('order', 0)
                )
                
                quiz_questions = lesson_data.get('quiz_questions', [])
                if quiz_questions:
                    quiz = Quiz.objects.create(
                        lesson=lesson,
                        questions=quiz_questions
                    )
        
        return course 

    def _generate_prompt_course(self, prompt, difficulty):
        """Generate a comprehensive course from a learning prompt"""
        # Create course with prompt as title
        course = Course.objects.create(
            title=prompt,
            description=f'AI-generated course: {prompt}',
            difficulty=difficulty,
            generation_type='prompt'
        )
        
        # Generate comprehensive course structure using AI
        course_structure = self.ai_service.generate_comprehensive_course_structure(prompt, difficulty)
        
        # Create modules and lessons
        for i, module_data in enumerate(course_structure.get('modules', [])):
            module = Module.objects.create(
                course=course,
                title=module_data['title'],
                order=i
            )
            
            for j, lesson_data in enumerate(module_data.get('lessons', [])):
                # Search for YouTube videos for this lesson
                youtube_video_id = None
                video_info = lesson_data.get('video_info', {})
                
                if lesson_data.get('type') == 'video':
                    search_term = lesson_data.get('youtube_search_term', lesson_data['title'])
                    print(f"Searching for videos with term: {search_term}")
                    
                    # Search for relevant YouTube videos
                    videos = self.youtube_service.search_youtube_videos(search_term, max_results=3)
                    
                    if videos:
                        # Use the first (most relevant) video
                        selected_video = videos[0]
                        youtube_video_id = selected_video['video_id']
                        video_info = {
                            'title': selected_video['title'],
                            'description': selected_video['description'],
                            'channel_title': selected_video['channel_title'],
                            'thumbnail': selected_video['thumbnail']
                        }
                        print(f"Found video: {selected_video['title']} (ID: {youtube_video_id})")
                    else:
                        print(f"No videos found for search term: {search_term}")
                
                lesson = Lesson.objects.create(
                    module=module,
                    title=lesson_data['title'],
                    lesson_type=lesson_data.get('type', 'video'),
                    duration=lesson_data.get('duration', 0),
                    order=j,
                    youtube_video_id=youtube_video_id,
                    chapter_timestamp=lesson_data.get('chapter_timestamp', '')
                )
                
                # Generate study notes for each lesson
                if lesson.lesson_type == 'video' and youtube_video_id:
                    study_notes = self.ai_service.generate_structured_study_notes(
                        lesson.title,
                        video_info=video_info
                    )
                    
                    StudyNote.objects.create(
                        lesson=lesson,
                        golden_notes=study_notes.get('golden_notes', []),
                        summaries=study_notes.get('summaries', []),
                        own_notes=study_notes.get('own_notes', ''),
                        content=study_notes.get('content', ''),
                        key_concepts=study_notes.get('key_concepts', []),
                        code_examples=study_notes.get('code_examples', []),
                        summary=study_notes.get('summary', '')
                    )
        
        return course 