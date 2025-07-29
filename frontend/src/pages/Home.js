import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Clock, Play, List, Trash2, Sparkles, Link, MessageSquare } from 'lucide-react';
import { generateCourse, getCourses, deleteCourse } from '../services/api';

const Home = () => {
  const [linkFormData, setLinkFormData] = useState({
    youtube_url: '',
    topic: '',
    difficulty: 'beginner'
  });
  const [promptFormData, setPromptFormData] = useState({
    prompt: '',
    difficulty: 'beginner'
  });
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState('link');
  const navigate = useNavigate();

  useEffect(() => {
    loadCourses();
    // Reset form data when component mounts
    setLinkFormData({
      youtube_url: '',
      topic: '',
      difficulty: 'beginner'
    });
    setPromptFormData({
      prompt: '',
      difficulty: 'beginner'
    });
    setGenerating(false);
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const data = await getCourses();
      setCourses(data);
    } catch (error) {
      console.error('Error loading courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCourse = async (courseId, e) => {
    e.stopPropagation(); // Prevent navigation when clicking delete button
    
    if (!window.confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
      return;
    }
    
    try {
      await deleteCourse(courseId);
      await loadCourses(); // Reload courses after deletion
    } catch (error) {
      console.error('Error deleting course:', error);
      alert('Error deleting course. Please try again.');
    }
  };

  const handleLinkSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!linkFormData.youtube_url.trim()) {
      alert('Please enter a YouTube URL');
      return;
    }
    
    setGenerating(true);
    
    try {
      console.log('Generating course from link... This may take 2-3 minutes for AI processing.');
      const course = await generateCourse(linkFormData);
      console.log('Course generated successfully:', course);
      // Reset form after successful generation
      setLinkFormData({ youtube_url: '', topic: '', difficulty: 'beginner' });
      await loadCourses();
      navigate(`/course/${course.id}`);
    } catch (error) {
      console.error('Error generating course:', error);
      if (error.message?.includes('timeout') || error.message?.includes('timeout')) {
        alert('Course generation is taking longer than expected. Please wait and try again in a few minutes.');
      } else if (error.message?.includes('Network Error')) {
        alert('Network error. Please check your connection and try again.');
      } else {
        alert('Error generating course. Please try again.');
      }
    } finally {
      setGenerating(false);
    }
  };

  const handlePromptSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!promptFormData.prompt.trim()) {
      alert('Please enter a learning prompt');
      return;
    }
    
    setGenerating(true);
    
    try {
      console.log('Generating course from prompt... This may take 3-4 minutes for AI processing.');
      // For prompt-based generation, we'll use a special endpoint or modify the existing one
      const courseData = {
        ...promptFormData,
        generation_type: 'prompt',
        youtube_url: null // No specific URL for prompt-based generation
      };
      const course = await generateCourse(courseData);
      console.log('Course generated successfully:', course);
      // Reset form after successful generation
      setPromptFormData({ prompt: '', difficulty: 'beginner' });
      await loadCourses();
      navigate(`/course/${course.id}`);
    } catch (error) {
      console.error('Error generating course:', error);
      if (error.message?.includes('timeout') || error.message?.includes('timeout')) {
        alert('Course generation is taking longer than expected. Please wait and try again in a few minutes.');
      } else if (error.message?.includes('Network Error')) {
        alert('Network error. Please check your connection and try again.');
      } else {
        alert('Error generating course. Please try again.');
      }
    } finally {
      setGenerating(false);
    }
  };

  const handleLinkInputChange = (e) => {
    setLinkFormData({
      ...linkFormData,
      [e.target.name]: e.target.value
    });
  };

  const handlePromptInputChange = (e) => {
    setPromptFormData({
      ...promptFormData,
      [e.target.name]: e.target.value
    });
  };

  const isPlaylistUrl = (url) => {
    return url.includes('playlist?list=') || url.includes('&list=');
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Transform Learning with
          <span className="text-primary-600"> AI-Powered Courses</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Generate structured courses from YouTube links or create custom learning paths with AI
        </p>
      </div>

      {/* Course Generation Tabs */}
      <div className="card mb-8">
        <div className="flex border-b border-gray-200 mb-6">
          <button
            onClick={() => setActiveTab('link')}
            className={`flex items-center gap-2 px-6 py-3 font-medium transition-colors ${
              activeTab === 'link'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Link className="h-5 w-5" />
            From YouTube Link
          </button>
          <button
            onClick={() => setActiveTab('prompt')}
            className={`flex items-center gap-2 px-6 py-3 font-medium transition-colors ${
              activeTab === 'prompt'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Sparkles className="h-5 w-5" />
            From Learning Prompt
          </button>
        </div>

        {/* Link-based Generation */}
        {activeTab === 'link' && (
          <div>
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
              <Link className="h-6 w-6 text-primary-600" />
              Generate from YouTube Link
            </h2>
            <form onSubmit={handleLinkSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    YouTube URL <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type="url"
                      name="youtube_url"
                      value={linkFormData.youtube_url}
                      onChange={handleLinkInputChange}
                      placeholder="https://www.youtube.com/watch?v=... or playlist URL"
                      className="input-field pr-10"
                      required
                    />
                    {linkFormData.youtube_url && (
                      <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        {isPlaylistUrl(linkFormData.youtube_url) ? (
                          <List className="h-5 w-5 text-blue-500" title="Playlist detected" />
                        ) : (
                          <Play className="h-5 w-5 text-green-500" title="Single video" />
                        )}
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Supports single videos and playlists. For playlists, each video becomes a module with chapters as lessons.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Topic (Optional)
                  </label>
                  <input
                    type="text"
                    name="topic"
                    value={linkFormData.topic}
                    onChange={handleLinkInputChange}
                    placeholder="e.g., React Hooks, Python Basics"
                    className="input-field"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Leave empty to use video title. For playlists, this becomes the course title.
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty Level
                </label>
                <select
                  name="difficulty"
                  value={linkFormData.difficulty}
                  onChange={handleLinkInputChange}
                  className="input-field"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={generating}
                className="btn-primary w-full md:w-auto"
              >
                {generating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generating Course (2-3 minutes)...
                  </>
                ) : (
                  'Generate from Link'
                )}
              </button>
            </form>
          </div>
        )}

        {/* Prompt-based Generation */}
        {activeTab === 'prompt' && (
          <div>
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary-600" />
              Generate from Learning Prompt
            </h2>
            <form onSubmit={handlePromptSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Learning Prompt <span className="text-red-500">*</span>
                </label>
                <textarea
                  name="prompt"
                  value={promptFormData.prompt}
                  onChange={handlePromptInputChange}
                  placeholder="e.g., Learn Python for Data Science, Master Digital Marketing, GCSE Mathematics"
                  className="input-field h-24 resize-none"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Describe what you want to learn. AI will create a comprehensive course structure and find relevant YouTube content.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Difficulty Level
                </label>
                <select
                  name="difficulty"
                  value={promptFormData.difficulty}
                  onChange={handlePromptInputChange}
                  className="input-field"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={generating}
                className="btn-primary w-full md:w-auto"
              >
                {generating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generating Course (3-4 minutes)...
                  </>
                ) : (
                  'Generate from Prompt'
                )}
              </button>
            </form>
          </div>
        )}
      </div>

      {/* Course List */}
      <div className="card">
        <h2 className="text-2xl font-semibold mb-6">Your Courses</h2>
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : courses.length === 0 ? (
          <div className="text-center py-8">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No courses yet. Generate your first course above!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.slice(0, 3).map((course) => (
              <div
                key={course.id}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer relative"
                onClick={() => navigate(`/course/${course.id}`)}
              >
                {/* Delete Button */}
                <button
                  onClick={(e) => handleDeleteCourse(course.id, e)}
                  className="absolute top-2 right-2 p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
                  title="Delete course"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
                
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 pr-8">
                    {course.title}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    course.difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
                    course.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {course.difficulty}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {course.description}
                </p>
                
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    <span>
                      {course.modules?.length || 0} modules
                    </span>
                  </div>
                  <div className="flex items-center">
                    {course.generation_type === 'prompt' ? (
                      <Sparkles className="h-4 w-4 mr-1 text-purple-500" />
                    ) : course.playlist_url ? (
                      <List className="h-4 w-4 mr-1 text-blue-500" />
                    ) : (
                      <Play className="h-4 w-4 mr-1 text-green-500" />
                    )}
                    <span>
                      {course.generation_type === 'prompt' ? 'AI Generated' : 
                       course.is_playlist ? 'Playlist' : 'Single Video'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Show message if there are more than 3 courses */}
        {courses.length > 3 && (
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              Showing 3 most recent courses. Delete some courses to see older ones.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home; 