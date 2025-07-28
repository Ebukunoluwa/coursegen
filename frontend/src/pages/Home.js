import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Clock } from 'lucide-react';
import { generateCourse, getCourses } from '../services/api';

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.youtube_url.trim()) {
      alert('Please enter a YouTube URL');
      return;
    }
    
    setGenerating(true);
    
    try {
      console.log('Generating course... This may take 1-2 minutes for AI processing.');
      const course = await generateCourse(formData);
      console.log('Course generated successfully:', course);
      setFormData({ youtube_url: '', topic: '', difficulty: 'beginner' });
      await loadCourses();
      navigate(`/course/${course.id}`);
    } catch (error) {
      console.error('Error generating course:', error);
      if (error.message?.includes('timeout')) {
        alert('Course generation is taking longer than expected. Please try again.');
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

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Transform YouTube Videos into
          <span className="text-primary-600"> Structured Courses</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Use AI to convert any YouTube video or topic into an interactive learning experience
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
              <input
                type="url"
                name="youtube_url"
                value={formData.youtube_url}
                onChange={handleInputChange}
                placeholder="https://www.youtube.com/watch?v=..."
                className="input-field"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Paste a YouTube URL to extract video content and chapters
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
                placeholder="e.g., Learn React, Python Basics"
                className="input-field"
              />
              <p className="text-sm text-gray-500 mt-1">
                Leave empty to use the video title as the course topic
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
            disabled={generating || (!formData.youtube_url && !formData.topic)}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {generating ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generating Course (1-2 minutes)...
              </div>
            ) : (
              'Generate Course'
            )}
          </button>
        </form>
      </div>

      {/* Course List */}
      <div>
        <h2 className="text-2xl font-semibold mb-6">Available Courses</h2>
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : courses.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No courses available yet. Generate your first course above!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <div key={course.id} className="card hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate(`/course/${course.id}`)}>
                <div className="flex items-center justify-between mb-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    course.difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
                    course.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {course.difficulty}
                  </span>
                  <div className="flex items-center text-sm text-gray-500">
                    <Clock className="h-4 w-4 mr-1" />
                    {course.modules?.length || 0} modules
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold mb-2">{course.title}</h3>
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">{course.description}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-sm text-gray-500">
                    <BookOpen className="h-4 w-4 mr-1" />
                    {course.modules?.reduce((total, module) => total + (module.lessons?.length || 0), 0) || 0} lessons
                  </div>
                  <button className="btn-primary text-sm px-3 py-1">
                    Start Learning
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home; 