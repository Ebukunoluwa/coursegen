import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes timeout for AI generation
});

// Course generation
export const generateCourse = async (data) => {
  try {
    const response = await api.post('/generate/', data);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Course listing
export const getCourses = async () => {
  try {
    const response = await api.get('/courses/');
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const getCourse = async (courseId) => {
  try {
    const response = await api.get(`/courses/${courseId}/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Module and lesson details
export const getModule = async (moduleId) => {
  try {
    const response = await api.get(`/modules/${moduleId}/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const getLesson = async (lessonId) => {
  try {
    const response = await api.get(`/lessons/${lessonId}/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Quiz functionality
export const getQuiz = async (lessonId) => {
  try {
    const response = await api.get(`/lessons/${lessonId}/quiz/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const submitQuiz = async (lessonId, answers, userId = 1) => {
  try {
    const response = await api.post(`/lessons/${lessonId}/submit-quiz/`, {
      answers,
      user_id: userId,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

// Progress tracking
export const getUserProgress = async (userId = 1) => {
  try {
    const response = await api.get(`/users/${userId}/progress/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const markLessonCompleted = async (lessonId, userId = 1) => {
  try {
    const response = await api.post(`/lessons/${lessonId}/complete/`, {
      user_id: userId,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const getDashboardStats = async (userId = 1) => {
  try {
    const response = await api.get(`/users/${userId}/dashboard/`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
}; 