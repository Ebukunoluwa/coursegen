import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Play, BookOpen, Clock, Navigation, FileText, CheckCircle } from 'lucide-react';
import { getCourse, markLessonCompleted } from '../services/api';
import VideoControls from '../components/VideoControls';

const CourseView = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);

  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const [currentModule, setCurrentModule] = useState(null);

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

  const handleTimeUpdate = (currentTime) => {
    try {
      // Update progress tracking
      if (selectedLesson && currentTime > 0) {
        // You can implement progress tracking here
        console.log(`Lesson ${selectedLesson.id} progress: ${currentTime}s`);
      }
    } catch (error) {
      console.error('Error updating time:', error);
    }
  };

  const handleLessonSelect = (lesson) => {
    try {
      setSelectedLesson(lesson);
      // Update current module when lesson is selected
      const lessonModule = course?.modules?.find(module => 
        module.lessons?.some(l => l.id === lesson.id)
      );
      setCurrentModule(lessonModule);
    } catch (error) {
      console.error('Error selecting lesson:', error);
    }
  };

  const getLessonIcon = (lessonType) => {
    try {
      switch (lessonType) {
        case 'video':
          return <Play className="h-4 w-4" />;
        case 'notes':
          return <FileText className="h-4 w-4" />;
        case 'quiz':
          return <CheckCircle className="h-4 w-4" />;
        default:
          return <Play className="h-4 w-4" />;
      }
    } catch (error) {
      console.error('Error getting lesson icon:', error);
      return <Play className="h-4 w-4" />;
    }
  };

  const getLessonTypeColor = (lessonType) => {
    try {
      switch (lessonType) {
        case 'video':
          return 'text-blue-600';
        case 'notes':
          return 'text-green-600';
        case 'quiz':
          return 'text-purple-600';
        default:
          return 'text-gray-600';
      }
    } catch (error) {
      console.error('Error getting lesson type color:', error);
      return 'text-gray-600';
    }
  };

  const handleStudyNotesClick = (lesson) => {
    try {
      if (lesson.lesson_type === 'notes') {
        navigate(`/lessons/${lesson.id}/study-notes`);
      }
    } catch (error) {
      console.error('Error navigating to study notes:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    try {
      if (!timestamp) return '';
      return timestamp;
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return '';
    }
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
      {/* Sidebar with proper scrolling */}
      <div className="w-80 bg-white shadow-lg flex flex-col">
        {/* Fixed header - Just course name and difficulty */}
        <div className="p-4 border-b flex-shrink-0">
          <h1 className="text-lg font-semibold text-gray-900 mb-2">{course.title}</h1>
          <div className="flex items-center">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              course.difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
              course.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {course.difficulty}
            </span>
          </div>
        </div>

        {/* Scrollable content - Takes most space */}
        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
          {course.modules?.map((module) => (
            <div key={module.id} className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">{module.title}</h3>
              <div className="space-y-2">
                {module.lessons?.map((lesson) => (
                  <button
                    key={lesson.id}
                    onClick={() => lesson.lesson_type === 'notes' ? handleStudyNotesClick(lesson) : handleLessonSelect(lesson)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedLesson?.id === lesson.id
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className={getLessonTypeColor(lesson.lesson_type)}>
                          {getLessonIcon(lesson.lesson_type)}
                        </span>
                        <span className="text-sm font-medium">{lesson.title}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {lesson.chapter_timestamp && lesson.lesson_type === 'video' && (
                          <div className="flex items-center space-x-1">
                            <Navigation className="h-3 w-3 text-blue-500" />
                            <span className="text-xs text-blue-600 font-medium">
                              {formatTimestamp(lesson.chapter_timestamp)}
                            </span>
                          </div>
                        )}
                        {lesson.duration > 0 && (
                          <>
                            <Clock className="h-3 w-3 text-gray-400" />
                            <span className="text-xs text-gray-500">
                              {Math.floor(lesson.duration / 60)}:{String(lesson.duration % 60).padStart(2, '0')}
                            </span>
                          </>
                        )}
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
            {/* Video Player with Controls - Only for video lessons */}
            {selectedLesson.lesson_type === 'video' && (
              <div className="bg-black">
                {(() => {
                  // For playlist videos, use the lesson's youtube_video_id
                  // For single videos, fall back to extracting from course.youtube_source
                  let videoId = selectedLesson?.youtube_video_id;
                  
                  if (!videoId && course.youtube_source) {
                    // Try to extract video ID from course source (for single videos)
                    const urlMatch = course.youtube_source.match(/[?&]v=([^&]+)/);
                    videoId = urlMatch ? urlMatch[1] : null;
                  }
                  
                  // Debug logging
                  console.log('Video ID extraction:', {
                    lessonVideoId: selectedLesson?.youtube_video_id,
                    courseSource: course.youtube_source,
                    extractedVideoId: videoId,
                    selectedLesson: selectedLesson
                  });
                  
                  return videoId ? (
                    <VideoControls 
                      key={`${videoId}-${selectedLesson?.id}`} // Force re-render when video changes
                      videoId={videoId}
                      timestamp={selectedLesson?.chapter_timestamp}
                      onTimeUpdate={handleTimeUpdate}
                    />
                  ) : (
                    <div className="aspect-video flex items-center justify-center text-white">
                      <div className="text-center">
                        <Play className="h-16 w-16 mx-auto mb-4 opacity-50" />
                        <p>No video available for this lesson</p>
                        <p className="text-sm text-gray-400 mt-2">
                          Video ID: {videoId || 'Not found'}
                        </p>
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}

            {/* Lesson Content */}
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    {/* Removed lesson title display */}
                  </div>
                  <button
                    onClick={handleLessonComplete}
                    disabled={completing}
                    className="btn-primary"
                  >
                    {completing ? 'Marking Complete...' : 'Mark Complete'}
                  </button>
                </div>

                {/* Content based on lesson type */}
                {selectedLesson.lesson_type === 'video' && (
                  <>
                    {/* Quiz Section for video lessons */}
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
                  </>
                )}

                {selectedLesson.lesson_type === 'notes' && (
                  <div className="card">
                    <div className="text-center py-8">
                      <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                      <h3 className="text-lg font-semibold mb-2">Study Notes</h3>
                      <p className="text-gray-600 mb-4">
                        Click on the study notes in the sidebar to view detailed notes for this lesson.
                      </p>
                      <button 
                        onClick={() => navigate(`/lessons/${selectedLesson.id}/study-notes`)}
                        className="btn-primary"
                      >
                        View Study Notes
                      </button>
                    </div>
                  </div>
                )}

                {selectedLesson.lesson_type === 'quiz' && (
                  <div className="card">
                    <div className="text-center py-8">
                      <CheckCircle className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                      <h3 className="text-lg font-semibold mb-2">Quiz</h3>
                      <p className="text-gray-600 mb-4">
                        Test your knowledge with this quiz based on the lesson content.
                      </p>
                      <button className="btn-primary">
                        Take Quiz
                      </button>
                    </div>
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