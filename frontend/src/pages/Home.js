import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Clock, Play, List, Trash2 } from 'lucide-react';
import { generateCourse, getCourses, deleteCourse } from '../services/api';

const Home = () => {
  const [formData, setFormData] = useState({
    youtube_url: '',
    topic: '',
    difficulty: 'beginner'
  });
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadCourses();
    // Reset form data when component mounts
    setFormData({
      youtube_url: '',
      topic: '',
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.youtube_url.trim()) {
      alert('Please enter a YouTube URL');
      return;
    }
    
    setGenerating(true);
    
    try {
      console.log('Generating course... This may take 2-3 minutes for AI processing.');
      const course = await generateCourse(formData);
      console.log('Course generated successfully:', course);
      // Reset form after successful generation
      setFormData({ youtube_url: '', topic: '', difficulty: 'beginner' });
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

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
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
          Transform YouTube Videos into
          <span className="text-primary-600"> Structured Courses</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Use AI to convert any YouTube video or playlist into an interactive learning experience
        </p>
      </div>

      {/* Course Generation Form */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold mb-6">Generate New Course</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                YouTube URL <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  type="url"
                  name="youtube_url"
                  value={formData.youtube_url}
                  onChange={handleInputChange}
                  placeholder="https://www.youtube.com/watch?v=... or playlist URL"
                  className="input-field pr-10"
                  required
                />
                {formData.youtube_url && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    {isPlaylistUrl(formData.youtube_url) ? (
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
                value={formData.topic}
                onChange={handleInputChange}
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
              value={formData.difficulty}
              onChange={handleInputChange}
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
              'Generate Course'
            )}
          </button>
        </form>
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
                    {course.playlist_url ? (
                      <List className="h-4 w-4 mr-1 text-blue-500" />
                    ) : (
                      <Play className="h-4 w-4 mr-1 text-green-500" />
                    )}
                    <span>
                      {course.is_playlist ? 'Playlist' : 'Single Video'}
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