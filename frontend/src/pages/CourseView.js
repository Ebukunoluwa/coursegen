import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Play, BookOpen, Clock, Navigation } from 'lucide-react';
import { getCourse, markLessonCompleted } from '../services/api';

const CourseView = () => {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);

  const loadCourse = useCallback(async () => {
    try {
      const data = await getCourse(courseId);
      setCourse(data);
      // Select first lesson by default
      if (data.modules?.[0]?.lessons?.[0]) {
        setSelectedLesson(data.modules[0].lessons[0]);
      }
    } catch (error) {
      console.error('Error loading course:', error);
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    loadCourse();
  }, [loadCourse]);

  const handleLessonComplete = async () => {
    if (!selectedLesson) return;
    
    setCompleting(true);
    try {
      await markLessonCompleted(selectedLesson.id);
      // Refresh course data
      await loadCourse();
    } catch (error) {
      console.error('Error marking lesson complete:', error);
    } finally {
      setCompleting(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    return timestamp;
  };

  const getVideoUrlWithTimestamp = (videoId, timestamp) => {
    if (!videoId) return '';
    if (!timestamp) return `https://www.youtube.com/embed/${videoId}`;
    const seconds = timestampToSeconds(timestamp);
    return `https://www.youtube.com/embed/${videoId}?start=${seconds}`;
  };

  const timestampToSeconds = (timestamp) => {
    if (!timestamp) return 0;
    const parts = timestamp.split(':');
    if (parts.length === 2) {
      const [minutes, seconds] = parts;
      return parseInt(minutes) * 60 + parseInt(seconds);
    } else if (parts.length === 3) {
      const [hours, minutes, seconds] = parts;
      return parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(seconds);
    }
    return 0;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Course not found</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white shadow-lg overflow-y-auto">
        <div className="p-6 border-b">
          <h1 className="text-xl font-semibold mb-2">{course.title}</h1>
          <p className="text-sm text-gray-600">{course.description}</p>
          <div className="flex items-center mt-3">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              course.difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
              course.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {course.difficulty}
            </span>
          </div>
        </div>

        <div className="p-4">
          {course.modules?.map((module) => (
            <div key={module.id} className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">{module.title}</h3>
              <div className="space-y-2">
                {module.lessons?.map((lesson) => (
                  <button
                    key={lesson.id}
                    onClick={() => setSelectedLesson(lesson)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedLesson?.id === lesson.id
                        ? 'bg-primary-50 border border-primary-200'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Play className="h-4 w-4 text-gray-400" />
                        <span className="text-sm font-medium">{lesson.title}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {lesson.chapter_timestamp && (
                          <div className="flex items-center space-x-1">
                            <Navigation className="h-3 w-3 text-blue-500" />
                            <span className="text-xs text-blue-600 font-medium">
                              {formatTimestamp(lesson.chapter_timestamp)}
                            </span>
                          </div>
                        )}
                        <Clock className="h-3 w-3 text-gray-400" />
                        <span className="text-xs text-gray-500">
                          {Math.floor(lesson.duration / 60)}:{String(lesson.duration % 60).padStart(2, '0')}
                        </span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {selectedLesson ? (
          <>
            {/* Video Player */}
            <div className="bg-black aspect-video">
              {selectedLesson.youtube_video_id ? (
                <iframe
                  src={getVideoUrlWithTimestamp(selectedLesson.youtube_video_id, selectedLesson.chapter_timestamp)}
                  title={selectedLesson.title}
                  className="w-full h-full"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              ) : (
                <div className="w-full h-full flex items-center justify-center text-white">
                  <div className="text-center">
                    <Play className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p>Video content will be displayed here</p>
                  </div>
                </div>
              )}
            </div>

            {/* Lesson Content */}
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-semibold">{selectedLesson.title}</h2>
                    {selectedLesson.chapter_timestamp && (
                      <p className="text-sm text-blue-600 mt-1">
                        <Navigation className="h-4 w-4 inline mr-1" />
                        Chapter starts at {formatTimestamp(selectedLesson.chapter_timestamp)}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={handleLessonComplete}
                    disabled={completing}
                    className="btn-primary"
                  >
                    {completing ? 'Marking Complete...' : 'Mark Complete'}
                  </button>
                </div>

                {/* AI Notes */}
                <div className="card mb-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <BookOpen className="h-5 w-5 mr-2" />
                    AI-Generated Notes
                  </h3>
                  <div className="prose max-w-none">
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {selectedLesson.ai_notes || 'AI-generated notes will appear here...'}
                    </p>
                  </div>
                </div>

                {/* Quiz Section */}
                {selectedLesson.quiz && (
                  <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Quiz</h3>
                    <p className="text-gray-600 mb-4">
                      Test your knowledge with this quiz based on the lesson content.
                    </p>
                    <button className="btn-primary">
                      Take Quiz
                    </button>
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <BookOpen className="h-12 w-12 mx-auto mb-4" />
              <p>Select a lesson to start learning</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CourseView; 