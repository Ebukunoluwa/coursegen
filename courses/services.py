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
        """Search for YouTube videos using the Data API with enhanced filtering"""
        if not self.api_key:
            return []
            
        try:
            # Enhanced search with multiple strategies
            search_strategies = [
                # Strategy 1: Exact search term
                search_term,
                # Strategy 2: Add "tutorial" for better educational content
                f"{search_term} tutorial",
                # Strategy 3: Add "explained" for detailed explanations
                f"{search_term} explained",
                # Strategy 4: Add "for beginners" for beginner-friendly content
                f"{search_term} for beginners",
                # Strategy 5: Just the main topic for broader results
                search_term.split()[0] if len(search_term.split()) > 1 else search_term
            ]
            
            all_videos = []
            
            for strategy in search_strategies:
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    'part': 'snippet',
                    'q': strategy,
                    'type': 'video',
                    'maxResults': max_results,
                    'order': 'relevance',
                    'videoDuration': 'medium',  # 4-20 minutes for good content
                    'videoDefinition': 'high',  # HD videos
                    'key': self.api_key
                }
                
                response = requests.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', []):
                        video_info = {
                            'video_id': item['id']['videoId'],
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'channel_title': item['snippet']['channelTitle'],
                            'published_at': item['snippet']['publishedAt'],
                            'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                            'search_strategy': strategy
                        }
                        all_videos.append(video_info)
                        
            # Remove duplicates based on video_id
            seen_videos = set()
            unique_videos = []
            
            for video in all_videos:
                if video['video_id'] not in seen_videos:
                    seen_videos.add(video['video_id'])
                    unique_videos.append(video)
            
            # Sort by relevance (exact matches first, then tutorial, explained, for beginners, main topic)
            def relevance_score(video):
                strategy = video.get('search_strategy', '')
                if strategy == search_term:
                    return 5
                elif 'tutorial' in strategy:
                    return 4
                elif 'explained' in strategy:
                    return 3
                elif 'for beginners' in strategy:
                    return 2
                elif len(strategy.split()) == 1:  # Single word searches
                    return 1
                return 0
            
            unique_videos.sort(key=relevance_score, reverse=True)
            
            # Return top results
            return unique_videos[:max_results]
                
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
            
        # ULTRA-COMPREHENSIVE prompt for detailed course generation
        prompt_text = f"""
        Create a COMPREHENSIVE and DETAILED learning course for: "{prompt}"
        Difficulty Level: {difficulty}
        
        This course must cover EVERY SINGLE ASPECT of the subject matter in depth. Leave no stone unturned.
        
        Follow this ULTRA-DETAILED process:
        
        1. DEEP TOPIC ANALYSIS:
        - Parse the learning intent and identify ALL core subject matter components
        - Extract skill level indicators and specific learning goals
        - Identify ALL prerequisite concepts and logical learning progression
        - Map out the ENTIRE knowledge domain systematically
        
        2. COMPREHENSIVE KNOWLEDGE MAPPING:
        - Break down the main topic into EVERY prerequisite concept
        - Map ALL concept dependencies (what must be learned before what)
        - Design detailed skill milestones and checkpoints
        - Identify ALL sub-topics, techniques, tools, and methodologies
        - Include both theoretical foundations and practical applications
        
        3. EXHAUSTIVE CONTENT STRATEGY:
        - Plan optimal learning sequence based on concept difficulty
        - Identify ALL potential knowledge gaps that need filling
        - Design comprehensive assessment points and practical applications
        - Include real-world examples, case studies, and industry best practices
        - Cover both beginner fundamentals and advanced techniques
        
        4. DETAILED COURSE STRUCTURE:
        - Group related concepts into logical modules (6-8 modules for comprehensive coverage)
        - Ensure each module has CLEAR and DETAILED learning objectives
        - Balance module length and complexity
        - Create smooth transitions between modules
        - Include both theoretical and practical modules
        
        5. GRANULAR LESSON PLANNING:
        - Break modules into detailed lesson chunks (4-6 lessons per module)
        - Sequence lessons for optimal knowledge building
        - Plan mix of theory, examples, practical application, and hands-on projects
        - Design appropriate pacing for {difficulty} level
        - Include assessment checkpoints and review sessions
        
        6. PRECISE YOUTUBE CONTENT CURATION:
        - For each lesson, provide SPECIFIC and TARGETED YouTube search terms
        - Focus on high-quality educational content from reputable channels
        - Include both theoretical and practical content
        - Suggest search terms that will find videos with EXCELLENT explanations
        - Ensure videos cover the EXACT topic being taught
        - Include multiple search variations to find the best content
        
        7. COMPREHENSIVE ASSESSMENT INTEGRATION:
        - Plan quiz placement for optimal retention
        - Design varied question types per topic
        - Create progressive difficulty in assessments
        - Plan final projects or practical applications
        - Include hands-on exercises and real-world projects
        
        8. DETAILED CONTENT REQUIREMENTS:
        - Each lesson must have a detailed description explaining what will be covered
        - Include specific learning outcomes for each lesson
        - Mention tools, technologies, or concepts that will be introduced
        - Include practical applications and real-world examples
        - Cover both theory and hands-on practice
        
        Format as JSON:
        {{
            "title": "Professional, engaging course title that clearly communicates comprehensive coverage",
            "description": "DETAILED course description that explains EVERYTHING students will learn and achieve",
            "modules": [
                {{
                    "title": "Detailed Module Title",
                    "description": "Comprehensive module description covering all aspects",
                    "lessons": [
                        {{
                            "title": "Detailed Lesson Title",
                            "description": "Comprehensive lesson description explaining exactly what will be covered, tools used, concepts introduced, and practical applications",
                            "type": "video",
                            "duration": 1800,
                            "youtube_search_term": "very specific search term that will find the exact video content needed",
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
        
        For YouTube search terms, use VERY SPECIFIC and TARGETED terms that will find high-quality educational videos.
        Examples: "python object oriented programming tutorial", "machine learning neural networks explained", "data science pandas numpy tutorial"
        
        IMPORTANT: 
        - Create a professional, engaging course title that clearly communicates COMPREHENSIVE coverage
        - Each lesson description must be DETAILED and explain exactly what will be learned
        - YouTube search terms must be SPECIFIC to find the exact content needed
        - Cover EVERY aspect of the subject matter - leave nothing out
        - Include both theoretical foundations and practical applications
        - Ensure videos are highly relevant to the specific lesson content
        
        Examples of comprehensive titles:
        - "Complete Python Programming Masterclass: From Beginner to Advanced with Real Projects"
        - "Digital Marketing Strategy: Complete Guide from Fundamentals to Expert Level"
        - "Data Science Fundamentals: Master Analytics, Machine Learning & AI Applications"
        - "Web Development Bootcamp: Full-Stack Mastery with Modern Technologies"
        
        Ensure the course is COMPREHENSIVE, DETAILED, and covers EVERY SINGLE ASPECT of the subject matter for {difficulty} level learners.
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
        if chapter_info and isinstance(chapter_info, dict) and chapter_info.get('lessons'):
            context += f"\n\nThis module contains the following lessons:"
            for i, lesson in enumerate(chapter_info['lessons'], 1):
                if isinstance(lesson, dict):
                    lesson_title = lesson.get('title', 'Unknown lesson')
                    timestamp = lesson.get('chapter_timestamp', '')
                else:
                    lesson_title = str(lesson)
                    timestamp = ''
                
                context += f"\n{i}. {lesson_title}"
                if timestamp:
                    context += f" (starts at {timestamp})"
        
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
        
        # Generate dynamic content based on lesson title
        lesson_lower = lesson_title.lower()
        
        if "python" in lesson_lower or "programming" in lesson_lower:
            golden_notes = [
                {
                    "title": "Python Fundamentals",
                    "explanation": "Core programming concepts including variables, data types, control structures, and functions. Understanding these fundamentals is essential for building any Python application.",
                    "examples": ["Variable assignment and data types", "Conditional statements and loops", "Function definition and calling"],
                    "key_points": ["Variables store data values", "Control flow manages program logic", "Functions organize reusable code"]
                },
                {
                    "title": "Object-Oriented Programming",
                    "explanation": "Programming paradigm that organizes code into objects containing data and methods. This approach promotes code reusability, maintainability, and scalability.",
                    "examples": ["Class definition and instantiation", "Inheritance and polymorphism", "Encapsulation and abstraction"],
                    "key_points": ["Classes define object blueprints", "Inheritance promotes code reuse", "Encapsulation protects data"]
                },
                {
                    "title": "Data Structures",
                    "explanation": "Organized ways to store and manage data efficiently. Different structures optimize for various operations like searching, insertion, and deletion.",
                    "examples": ["Lists, tuples, and dictionaries", "Sets for unique collections", "Custom data structures"],
                    "key_points": ["Choose structures based on use case", "Understand time complexity", "Optimize for common operations"]
                }
            ]
            summaries = [
                "Python fundamentals include variables, data types, and control structures",
                "Object-oriented programming organizes code into reusable classes and objects",
                "Data structures optimize data storage and retrieval operations",
                "Functions organize code into reusable, modular components",
                "Error handling ensures robust and reliable applications",
                "Libraries and frameworks accelerate development processes"
            ]
        elif "data" in lesson_lower or "analytics" in lesson_lower:
            golden_notes = [
                {
                    "title": "Data Analysis Fundamentals",
                    "explanation": "Systematic approach to examining, cleaning, transforming, and modeling data to discover useful information and support decision-making processes.",
                    "examples": ["Statistical analysis and visualization", "Data cleaning and preprocessing", "Exploratory data analysis"],
                    "key_points": ["Start with data exploration", "Clean and validate data", "Use appropriate analysis methods"]
                },
                {
                    "title": "Data Visualization",
                    "explanation": "Graphical representation of data to communicate insights effectively. Good visualizations make complex data accessible and actionable.",
                    "examples": ["Charts, graphs, and dashboards", "Interactive visualizations", "Storytelling with data"],
                    "key_points": ["Choose appropriate chart types", "Design for clarity and impact", "Tell compelling data stories"]
                },
                {
                    "title": "Statistical Methods",
                    "explanation": "Mathematical techniques for analyzing data patterns, relationships, and trends. Statistics provide the foundation for data-driven decision making.",
                    "examples": ["Descriptive and inferential statistics", "Hypothesis testing", "Regression analysis"],
                    "key_points": ["Understand basic statistical concepts", "Apply appropriate tests", "Interpret results correctly"]
                }
            ]
            summaries = [
                "Data analysis involves systematic examination and transformation of data",
                "Data visualization communicates insights through graphical representations",
                "Statistical methods provide mathematical foundation for analysis",
                "Data cleaning ensures quality and reliability of analysis",
                "Exploratory analysis reveals patterns and relationships",
                "Effective visualization tells compelling data stories"
            ]
        elif "machine learning" in lesson_lower or "ai" in lesson_lower:
            golden_notes = [
                {
                    "title": "Machine Learning Basics",
                    "explanation": "Subset of artificial intelligence that enables systems to learn and improve from experience without explicit programming. ML algorithms identify patterns in data to make predictions.",
                    "examples": ["Supervised and unsupervised learning", "Classification and regression tasks", "Model training and evaluation"],
                    "key_points": ["Algorithms learn from data patterns", "Different types for different tasks", "Evaluation metrics measure performance"]
                },
                {
                    "title": "Neural Networks",
                    "explanation": "Computing systems inspired by biological neural networks. These networks process information through interconnected nodes and can learn complex patterns.",
                    "examples": ["Deep learning architectures", "Convolutional neural networks", "Recurrent neural networks"],
                    "key_points": ["Multiple layers process information", "Weights adjust during training", "Can learn complex patterns"]
                },
                {
                    "title": "Model Evaluation",
                    "explanation": "Systematic assessment of machine learning model performance using various metrics and validation techniques to ensure reliable predictions.",
                    "examples": ["Accuracy, precision, and recall", "Cross-validation techniques", "Bias-variance tradeoff"],
                    "key_points": ["Use appropriate evaluation metrics", "Validate on unseen data", "Balance bias and variance"]
                }
            ]
            summaries = [
                "Machine learning enables systems to learn from data without explicit programming",
                "Neural networks process information through interconnected nodes",
                "Model evaluation ensures reliable and accurate predictions",
                "Different algorithms suit different types of problems",
                "Training data quality directly impacts model performance",
                "Regularization techniques prevent overfitting"
            ]
        else:
            # Generic business/management content
            golden_notes = [
                {
                    "title": "Strategic Planning",
                    "explanation": "Systematic process of defining organizational direction and making decisions about allocating resources to pursue this strategy. Effective planning aligns actions with long-term goals.",
                    "examples": ["SWOT analysis and market research", "Goal setting and KPI development", "Resource allocation and budgeting"],
                    "key_points": ["Aligns actions with objectives", "Involves stakeholder input", "Requires regular review and adjustment"]
                },
                {
                    "title": "Performance Management",
                    "explanation": "Continuous process of setting objectives, assessing progress, and providing ongoing coaching and feedback to ensure employees meet their goals and career objectives.",
                    "examples": ["Goal setting and tracking", "Regular feedback and coaching", "Performance reviews and development"],
                    "key_points": ["Set clear, measurable objectives", "Provide regular feedback", "Support continuous development"]
                },
                {
                    "title": "Change Management",
                    "explanation": "Systematic approach to dealing with organizational change, including preparing, supporting, and helping individuals and teams adapt to new processes, technologies, or structures.",
                    "examples": ["Communication and stakeholder engagement", "Training and support programs", "Monitoring and reinforcement"],
                    "key_points": ["Communicate vision and benefits", "Provide training and support", "Monitor progress and adjust"]
                }
            ]
            summaries = [
                "Strategic planning aligns actions with long-term organizational goals",
                "Performance management ensures continuous improvement and development",
                "Change management supports successful organizational transitions",
                "Effective communication is essential for successful implementation",
                "Regular monitoring and feedback drive continuous improvement",
                "Stakeholder engagement increases buy-in and success rates"
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

    def generate_module_notes(self, module_title, module):
        """Generate comprehensive module notes with overview, key concepts, and detailed content"""
        cache_key = f"module_notes_{module_title}_{module.id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        if not self.client:
            mock_notes = self._generate_mock_module_notes(module_title, module)
            self._cache[cache_key] = mock_notes
            return mock_notes
        
        # Get module context
        lessons = module.lessons.all()
        lesson_titles = [lesson.title for lesson in lessons]
        lesson_count = len(lessons)
        
        # Create comprehensive context
        context = f"""
        Module Title: {module_title}
        Module Description: {module.course.description}
        Course Title: {module.course.title}
        Number of Lessons: {lesson_count}
        Lesson Titles: {', '.join(lesson_titles)}
        """
        
        # Generate comprehensive module notes using a simpler approach like YouTube courses
        module_notes_prompt = f"""
        {context}
        
        Create COMPREHENSIVE MODULE NOTES for this entire module. This should cover all aspects of the module including:
        
        1. MODULE OVERVIEW: A comprehensive overview of what this module covers, its learning objectives, and its importance in the overall course.
        
        2. KEY CONCEPTS: A detailed list of all key concepts covered in this module with explanations.
        
        3. GOLDEN NOTES: Deep, comprehensive explanations of the main concepts covered in this module (5-8 concept cards).
        
        4. SUMMARIES: Quick, scannable bullet points summarizing the key takeaways from this module (8-12 points).
        
        5. ADDITIONAL RESOURCES: Suggested additional resources, tools, and references for further learning.
        
        Format the response as a comprehensive study guide with clear sections and detailed explanations.
        Make the content comprehensive, educational, and suitable for {module.course.difficulty} level learners.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": module_notes_prompt}],
                temperature=0.3,
                max_tokens=1500,
                timeout=30
            )
            
            content = response.choices[0].message.content.strip()
            
            # Use mock notes as fallback and enhance with AI content
            mock_notes = self._generate_mock_module_notes(module_title, module)
            
            # Create enhanced module notes structure
            enhanced_notes = {
                'overview': mock_notes.get('overview', ''),
                'key_concepts': mock_notes.get('key_concepts', []),
                'golden_notes': mock_notes.get('golden_notes', []),
                'summaries': mock_notes.get('summaries', []),
                'additional_resources': mock_notes.get('additional_resources', []),
                'content': f"# 📚 {module_title} - Module Study Guide\n\n{content}",
                'own_notes': ""
            }
            
            self._cache[cache_key] = enhanced_notes
            return enhanced_notes
            
        except Exception as e:
            print(f"Error generating module notes: {e}")
            mock_notes = self._generate_mock_module_notes(module_title, module)
            self._cache[cache_key] = mock_notes
            return mock_notes

    def _generate_mock_module_notes(self, module_title, module):
        """Generate mock module notes for comprehensive coverage"""
        # Generate dynamic content based on module title
        module_lower = module_title.lower()
        
        if "foundation" in module_lower or "fundamental" in module_lower:
            overview = f"Comprehensive foundation module covering all essential concepts and principles. This module establishes the core knowledge base required for advanced learning in {module.course.title}."
            key_concepts = [
                {"concept": "Core Principles", "explanation": "Fundamental principles and basic concepts that form the foundation of the subject"},
                {"concept": "Essential Tools", "explanation": "Key tools, technologies, and platforms used in this field"},
                {"concept": "Basic Terminology", "explanation": "Important terms and definitions that students need to understand"}
            ]
            golden_notes = [
                {
                    "title": "Foundation Concepts",
                    "explanation": "Core foundational concepts that provide the building blocks for all advanced topics. Understanding these fundamentals is essential for success in the field.",
                    "examples": ["Basic principles and theories", "Fundamental methodologies", "Core terminology and definitions"],
                    "key_points": ["Establish solid foundation", "Understand core principles", "Master basic terminology"]
                },
                {
                    "title": "Essential Tools and Technologies",
                    "explanation": "Critical tools, software, and technologies that are industry-standard in this field. Students will learn to set up their environment and use key tools effectively.",
                    "examples": ["Development environments", "Industry-standard software", "Key platforms and tools"],
                    "key_points": ["Set up development environment", "Master essential tools", "Understand industry standards"]
                }
            ]
        elif "intermediate" in module_lower or "advanced" in module_lower:
            overview = f"Intermediate to advanced module focusing on practical applications, advanced techniques, and real-world implementation. This module builds on foundational knowledge with sophisticated approaches."
            key_concepts = [
                {"concept": "Advanced Techniques", "explanation": "Sophisticated methods and approaches used by industry professionals"},
                {"concept": "Practical Applications", "explanation": "Real-world implementation and hands-on applications"},
                {"concept": "Problem-Solving", "explanation": "Strategies for identifying and resolving complex challenges"}
            ]
            golden_notes = [
                {
                    "title": "Advanced Techniques and Methods",
                    "explanation": "Sophisticated techniques and methodologies used by industry professionals. These advanced approaches enable students to tackle complex problems and create high-quality solutions.",
                    "examples": ["Advanced methodologies", "Professional techniques", "Industry best practices"],
                    "key_points": ["Master advanced techniques", "Apply professional methods", "Implement best practices"]
                },
                {
                    "title": "Real-World Applications",
                    "explanation": "Practical applications and hands-on implementation of concepts in real-world scenarios. Students will learn to apply their knowledge to solve actual problems.",
                    "examples": ["Case studies and examples", "Practical implementations", "Industry scenarios"],
                    "key_points": ["Apply knowledge practically", "Solve real problems", "Implement solutions"]
                }
            ]
        elif "mastery" in module_lower or "project" in module_lower:
            overview = f"Mastery-level module focusing on comprehensive projects, complex applications, and professional-level implementations. This module demonstrates complete proficiency and industry readiness."
            key_concepts = [
                {"concept": "Project Implementation", "explanation": "Complete project development from planning to deployment"},
                {"concept": "Complex Problem Solving", "explanation": "Advanced problem-solving strategies for sophisticated challenges"},
                {"concept": "Professional Standards", "explanation": "Industry standards and professional development requirements"}
            ]
            golden_notes = [
                {
                    "title": "Complete Project Implementation",
                    "explanation": "Comprehensive project development covering all aspects from initial planning to final deployment. Students will build complete, professional-level applications using all learned concepts.",
                    "examples": ["Full project lifecycle", "Professional development", "Industry-standard implementation"],
                    "key_points": ["Complete project development", "Professional implementation", "Industry standards"]
                },
                {
                    "title": "Advanced Problem Solving",
                    "explanation": "Sophisticated problem-solving strategies for complex challenges and real-world scenarios. Students will learn to analyze and resolve advanced problems using professional methodologies.",
                    "examples": ["Complex scenario analysis", "Advanced troubleshooting", "Professional problem-solving"],
                    "key_points": ["Analyze complex problems", "Apply advanced strategies", "Implement professional solutions"]
                }
            ]
        else:
            # Generic module content
            overview = f"Comprehensive module covering essential concepts and practical applications in {module.course.title}. This module provides both theoretical understanding and hands-on experience."
            key_concepts = [
                {"concept": "Core Concepts", "explanation": "Essential concepts and principles covered in this module"},
                {"concept": "Practical Applications", "explanation": "Real-world applications and hands-on implementation"},
                {"concept": "Best Practices", "explanation": "Industry best practices and professional standards"}
            ]
            golden_notes = [
                {
                    "title": "Module Overview",
                    "explanation": "Comprehensive overview of all concepts and techniques covered in this module. Students will gain both theoretical understanding and practical skills.",
                    "examples": ["Concept explanations", "Practical demonstrations", "Real-world examples"],
                    "key_points": ["Understand core concepts", "Apply practical skills", "Follow best practices"]
                },
                {
                    "title": "Advanced Applications",
                    "explanation": "Advanced applications and sophisticated techniques that build on foundational knowledge. Students will learn professional-level skills and methodologies.",
                    "examples": ["Advanced techniques", "Professional applications", "Industry methodologies"],
                    "key_points": ["Master advanced techniques", "Apply professional skills", "Implement industry standards"]
                }
            ]
        
        summaries = [
            f"Comprehensive coverage of {module_title} with detailed explanations and practical applications",
            "Essential concepts and principles that form the foundation for advanced learning",
            "Hands-on practical applications with real-world examples and case studies",
            "Industry best practices and professional standards for effective implementation",
            "Advanced techniques and methodologies used by industry professionals",
            "Problem-solving strategies for complex challenges and real-world scenarios",
            "Complete project implementation from planning to deployment",
            "Professional development and career advancement opportunities"
        ]
        
        additional_resources = [
            {
                "title": "Additional Reading Materials",
                "description": "Comprehensive reading materials and references for deeper understanding",
                "url": ""
            },
            {
                "title": "Practice Exercises",
                "description": "Hands-on exercises and practice problems to reinforce learning",
                "url": ""
            },
            {
                "title": "Industry Resources",
                "description": "Professional resources and industry-standard tools for practical application",
                "url": ""
            }
        ]
        
        return {
            'overview': overview,
            'key_concepts': key_concepts,
            'golden_notes': golden_notes,
            'summaries': summaries,
            'additional_resources': additional_resources,
            'content': f"# 📚 {module_title} - Module Study Guide\n\n## Overview\n{overview}\n\n## Key Concepts\n{self._format_key_concepts(key_concepts)}\n\n## Golden Notes\n{self._format_golden_notes(golden_notes)}\n\n## Summaries\n{self._format_summaries(summaries)}",
            'own_notes': ""
        }

    def _format_key_concepts(self, key_concepts):
        """Format key concepts for display"""
        if not key_concepts:
            return ""
        
        formatted = ""
        for concept in key_concepts:
            formatted += f"### {concept.get('concept', 'Unknown Concept')}\n"
            formatted += f"{concept.get('explanation', '')}\n\n"
        
        return formatted

    def _generate_mock_comprehensive_structure(self, prompt, difficulty):
        """Generate mock comprehensive course structure for prompt-based generation"""
        # Generate intuitive title based on prompt
        if "python" in prompt.lower():
            title = "Complete Python Programming Masterclass"
        elif "data science" in prompt.lower() or "data" in prompt.lower():
            title = "Data Science Fundamentals: From Beginner to Pro"
        elif "machine learning" in prompt.lower() or "ml" in prompt.lower():
            title = "Machine Learning Engineering: Complete Roadmap"
        elif "ads" in prompt.lower() or "advertising" in prompt.lower():
            title = "Digital Advertising Strategy: Complete Guide"
        elif "marketing" in prompt.lower():
            title = "Digital Marketing Mastery: Comprehensive Course"
        elif "web" in prompt.lower() or "development" in prompt.lower():
            title = "Web Development Bootcamp: Full-Stack Mastery"
        elif "javascript" in prompt.lower():
            title = "JavaScript Programming: Complete Developer Course"
        elif "react" in prompt.lower():
            title = "React.js Development: Modern Web Applications"
        elif "node" in prompt.lower():
            title = "Node.js Backend Development: Server-Side Mastery"
        elif "sql" in prompt.lower() or "database" in prompt.lower():
            title = "SQL Database Management: Complete Course"
        elif "excel" in prompt.lower():
            title = "Microsoft Excel Mastery: Data Analysis & Automation"
        elif "photoshop" in prompt.lower():
            title = "Adobe Photoshop: Digital Design Mastery"
        elif "video" in prompt.lower() or "editing" in prompt.lower():
            title = "Video Editing & Production: Complete Course"
        elif "photography" in prompt.lower():
            title = "Digital Photography: From Beginner to Professional"
        elif "business" in prompt.lower():
            title = "Business Strategy & Entrepreneurship: Complete Guide"
        elif "finance" in prompt.lower():
            title = "Personal Finance & Investment: Smart Money Management"
        elif "cooking" in prompt.lower() or "culinary" in prompt.lower():
            title = "Culinary Arts: Cooking Mastery from Basics to Advanced"
        elif "fitness" in prompt.lower() or "workout" in prompt.lower():
            title = "Fitness & Nutrition: Complete Health & Wellness Guide"
        elif "language" in prompt.lower() or "spanish" in prompt.lower() or "french" in prompt.lower():
            title = "Language Learning: Complete Communication Mastery"
        else:
            # Generic but professional title
            title = f"Complete {prompt.title()} Mastery Course"
        
        return {
            "title": title,
            "description": f"COMPREHENSIVE {prompt} course designed for {difficulty} level learners. This detailed course covers EVERY aspect of the subject matter, from fundamental concepts to advanced techniques. Students will master essential principles, practical applications, real-world examples, industry best practices, and hands-on projects through structured learning modules with comprehensive assessments and expert guidance.",
            "modules": [
                {
                    "title": "Foundation Fundamentals",
                    "description": "Comprehensive introduction covering all basic concepts, terminology, and essential principles. This module establishes the core knowledge base required for advanced learning.",
                    "lessons": [
                        {
                            "title": "Complete Introduction and Overview",
                            "description": "Comprehensive introduction to the subject matter covering all fundamental concepts, key terminology, learning objectives, and course roadmap. Students will understand the scope, importance, and practical applications of this field.",
                            "type": "video",
                            "duration": 2400,
                            "youtube_search_term": f"{prompt} introduction tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Complete Introduction Video",
                                "description": "Comprehensive introduction covering all fundamental concepts and learning objectives"
                            }
                        },
                        {
                            "title": "Core Principles and Fundamentals",
                            "description": "Deep dive into the core principles, fundamental concepts, and essential building blocks. Students will master the foundational knowledge required for all advanced topics and practical applications.",
                            "type": "video",
                            "duration": 2700,
                            "youtube_search_term": f"{prompt} basics tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Core Principles Video",
                                "description": "Comprehensive coverage of fundamental principles and core concepts"
                            }
                        },
                        {
                            "title": "Essential Tools and Technologies",
                            "description": "Comprehensive overview of all essential tools, technologies, software, and platforms used in this field. Students will learn to set up their development environment and understand industry-standard tools.",
                            "type": "video",
                            "duration": 2100,
                            "youtube_search_term": f"{prompt} tools tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Essential Tools Video",
                                "description": "Complete guide to essential tools and technologies"
                            }
                        }
                    ]
                },
                {
                    "title": "Intermediate Concepts and Techniques",
                    "description": "Building on foundational knowledge with intermediate concepts, advanced techniques, and practical applications. This module focuses on real-world implementation and industry best practices.",
                    "lessons": [
                        {
                            "title": "Advanced Techniques and Methods",
                            "description": "Comprehensive coverage of advanced techniques, methodologies, and best practices. Students will learn sophisticated approaches and industry-standard methods for solving complex problems.",
                            "type": "video",
                            "duration": 3000,
                            "youtube_search_term": f"{prompt} advanced tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Advanced Techniques Video",
                                "description": "Comprehensive guide to advanced techniques and methodologies"
                            }
                        },
                        {
                            "title": "Practical Applications and Real-World Examples",
                            "description": "Hands-on practical applications with real-world examples, case studies, and industry scenarios. Students will apply their knowledge to solve actual problems and understand practical implementation.",
                            "type": "video",
                            "duration": 3300,
                            "youtube_search_term": f"{prompt} examples tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Practical Applications Video",
                                "description": "Comprehensive practical applications with real-world examples"
                            }
                        },
                        {
                            "title": "Problem-Solving and Troubleshooting",
                            "description": "Comprehensive problem-solving strategies, troubleshooting techniques, and debugging methods. Students will learn to identify, analyze, and resolve common issues and challenges.",
                            "type": "video",
                            "duration": 2400,
                            "youtube_search_term": f"{prompt} problems tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Problem-Solving Video",
                                "description": "Complete guide to problem-solving and troubleshooting techniques"
                            }
                        }
                    ]
                },
                {
                    "title": "Advanced Implementation and Optimization",
                    "description": "Advanced implementation strategies, optimization techniques, and performance enhancement methods. This module covers expert-level skills and industry best practices.",
                    "lessons": [
                        {
                            "title": "Expert-Level Techniques and Strategies",
                            "description": "Master-level techniques, advanced strategies, and expert approaches used by industry professionals. Students will learn sophisticated methods for complex scenarios and high-performance applications.",
                            "type": "video",
                            "duration": 3600,
                            "youtube_search_term": f"{prompt} expert tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Expert Techniques Video",
                                "description": "Comprehensive expert-level techniques and advanced strategies"
                            }
                        },
                        {
                            "title": "Performance Optimization and Best Practices",
                            "description": "Comprehensive optimization techniques, performance enhancement strategies, and industry best practices. Students will learn to maximize efficiency, improve performance, and implement professional standards.",
                            "type": "video",
                            "duration": 3000,
                            "youtube_search_term": f"{prompt} optimization tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Optimization Video",
                                "description": "Complete guide to performance optimization and best practices"
                            }
                        },
                        {
                            "title": "Industry Standards and Professional Development",
                            "description": "Industry standards, professional development strategies, and career advancement techniques. Students will understand professional requirements, industry expectations, and career growth opportunities.",
                            "type": "video",
                            "duration": 2700,
                            "youtube_search_term": f"{prompt} professional tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Industry Standards Video",
                                "description": "Comprehensive guide to industry standards and professional development"
                            }
                        }
                    ]
                },
                {
                    "title": "Mastery and Real-World Projects",
                    "description": "Comprehensive mastery through real-world projects, complex applications, and industry-level implementations. This module demonstrates complete proficiency and professional capabilities.",
                    "lessons": [
                        {
                            "title": "Complete Real-World Project Implementation",
                            "description": "Comprehensive real-world project covering all aspects from planning to deployment. Students will build a complete, professional-level application using all learned concepts and techniques.",
                            "type": "video",
                            "duration": 4200,
                            "youtube_search_term": f"{prompt} project tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Real-World Project Video",
                                "description": "Complete real-world project implementation from start to finish"
                            }
                        },
                        {
                            "title": "Advanced Case Studies and Complex Scenarios",
                            "description": "Advanced case studies, complex scenarios, and challenging applications. Students will analyze and solve sophisticated problems using advanced techniques and professional methodologies.",
                            "type": "video",
                            "duration": 3600,
                            "youtube_search_term": f"{prompt} case studies tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Advanced Case Studies Video",
                                "description": "Comprehensive advanced case studies and complex scenarios"
                            }
                        },
                        {
                            "title": "Final Mastery Assessment and Portfolio Development",
                            "description": "Comprehensive final assessment, portfolio development, and mastery demonstration. Students will showcase their complete understanding and professional capabilities through comprehensive evaluation.",
                            "type": "video",
                            "duration": 3000,
                            "youtube_search_term": f"{prompt} mastery tutorial",
                            "chapter_timestamp": "00:00",
                            "video_info": {
                                "title": "Final Assessment Video",
                                "description": "Complete final mastery assessment and portfolio development"
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
        # Generate comprehensive course structure using AI
        course_structure = self.ai_service.generate_comprehensive_course_structure(prompt, difficulty)
        
        # Use AI-generated title and description instead of raw prompt
        course_title = course_structure.get('title', f'Complete {prompt} Course')
        course_description = course_structure.get('description', f'Comprehensive course on {prompt} for {difficulty} level learners')
        
        # Create course with AI-generated title
        course = Course.objects.create(
            title=course_title,
            description=course_description,
            difficulty=difficulty,
            generation_type='prompt'
        )
        
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
                
                # Generate study notes for each lesson (for all lesson types)
                if lesson.lesson_type == 'video':
                    # For video lessons, use video info if available
                    if youtube_video_id and video_info:
                        study_notes = self.ai_service.generate_structured_study_notes(
                            lesson.title,
                            video_info=video_info
                        )
                    else:
                        # Generate notes based on lesson title and course context
                        study_notes = self.ai_service.generate_structured_study_notes(
                            lesson.title,
                            video_info={
                                'title': lesson.title,
                                'description': f"Lesson on {lesson.title} from {course.title}",
                                'channel_title': 'Course Content'
                            }
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
                elif lesson.lesson_type == 'notes':
                    # For notes lessons, generate comprehensive study materials
                    study_notes = self.ai_service.generate_structured_study_notes(
                        lesson.title,
                        video_info={
                            'title': lesson.title,
                            'description': f"Comprehensive study materials for {lesson.title}",
                            'channel_title': 'Study Materials'
                        }
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
            
            # Create a notes lesson for each module (like YouTube link courses)
            notes_lesson = Lesson.objects.create(
                module=module,
                title=f"📝 Complete Study Notes - {module.title}",
                lesson_type='notes',
                order=len(module_data.get('lessons', []))
            )
            
            # Generate comprehensive study notes for the module
            study_notes = self.ai_service.generate_structured_study_notes(
                f"Complete {module.title} Study Guide",
                video_info={
                    'title': module.title,
                    'description': f"Comprehensive study materials for {module.title} from {course.title}",
                    'channel_title': 'Course Content'
                },
                chapter_info={'title': module.title, 'lessons': [{'title': lesson.title} for lesson in module.lessons.all()]}
            )
            
            # Create StudyNote object for the notes lesson
            StudyNote.objects.create(
                lesson=notes_lesson,
                golden_notes=study_notes.get('golden_notes', []),
                summaries=study_notes.get('summaries', []),
                own_notes=study_notes.get('own_notes', ''),
                content=study_notes.get('content', ''),
                key_concepts=study_notes.get('key_concepts', []),
                code_examples=study_notes.get('code_examples', []),
                summary=study_notes.get('summary', '')
            )
            
            # Generate comprehensive module notes for each module
            module_notes = self.ai_service.generate_module_notes(module.title, module)
            
            # Create ModuleNote object
            from .models import ModuleNote
            ModuleNote.objects.create(
                module=module,
                overview=module_notes.get('overview', ''),
                key_concepts=module_notes.get('key_concepts', []),
                golden_notes=module_notes.get('golden_notes', []),
                summaries=module_notes.get('summaries', []),
                additional_resources=module_notes.get('additional_resources', []),
                content=module_notes.get('content', ''),
                own_notes=module_notes.get('own_notes', '')
            )
        
        return course
        
        return course 