import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, BookOpen, CheckCircle, Clock, Target } from 'lucide-react';
import { getDashboardStats, getUserProgress } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsData, progressData] = await Promise.all([
        getDashboardStats(),
        getUserProgress()
      ]);
      setStats(statsData);
      setProgress(progressData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Your Learning Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <BookOpen className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed Lessons</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.completed_lessons || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completion Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.completion_percentage || 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Target className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Average Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.average_score || 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Courses</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.active_courses?.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Active Courses */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-6">Active Courses</h2>
        {stats?.active_courses?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stats.active_courses.map((course) => (
              <div
                key={course.id}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/course/${course.id}`)}
              >
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
                
                <h3 className="font-semibold mb-2">{course.title}</h3>
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                  {course.description}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-sm text-gray-500">
                    <BookOpen className="h-4 w-4 mr-1" />
                    {course.modules?.reduce((total, module) => total + (module.lessons?.length || 0), 0) || 0} lessons
                  </div>
                  <button className="btn-primary text-sm px-3 py-1">
                    Continue
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No active courses yet. Start learning to see your progress here!</p>
          </div>
        )}
      </div>

      {/* Recent Progress */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-6">Recent Progress</h2>
        {progress.length > 0 ? (
          <div className="space-y-4">
            {progress.slice(0, 10).map((item) => (
              <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-medium">{item.lesson_title}</p>
                    <p className="text-sm text-gray-600">
                      {item.course_title} • {item.module_title}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  {item.quiz_score !== null && (
                    <p className="text-sm font-medium text-gray-900">
                      Quiz Score: {item.quiz_score}%
                    </p>
                  )}
                  <p className="text-xs text-gray-500">
                    {new Date(item.completed_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No progress recorded yet. Complete some lessons to see your activity here!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 