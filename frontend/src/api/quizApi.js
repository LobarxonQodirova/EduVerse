import api from './axiosConfig';

const quizApi = {
  // Quizzes
  getQuizzes: (params = {}) =>
    api.get('/quizzes/', { params }),

  getQuizDetail: (quizId) =>
    api.get(`/quizzes/${quizId}/`),

  createQuiz: (data) =>
    api.post('/quizzes/', data),

  updateQuiz: (quizId, data) =>
    api.patch(`/quizzes/${quizId}/`, data),

  deleteQuiz: (quizId) =>
    api.delete(`/quizzes/${quizId}/`),

  // Quiz attempts
  startAttempt: (quizId) =>
    api.post(`/quizzes/${quizId}/start_attempt/`),

  submitAttempt: (quizId, attemptId, responses) =>
    api.post(`/quizzes/${quizId}/attempts/${attemptId}/submit/`, { responses }),

  getMyAttempts: (quizId) =>
    api.get(`/quizzes/${quizId}/my_attempts/`),

  // Questions
  getQuestions: (quizId) =>
    api.get(`/quizzes/${quizId}/questions/`),

  createQuestion: (quizId, data) =>
    api.post(`/quizzes/${quizId}/questions/`, data),

  updateQuestion: (quizId, questionId, data) =>
    api.put(`/quizzes/${quizId}/questions/${questionId}/`, data),

  deleteQuestion: (quizId, questionId) =>
    api.delete(`/quizzes/${quizId}/questions/${questionId}/`),

  // Answers
  getAnswers: (questionId) =>
    api.get(`/quizzes/questions/${questionId}/answers/`),

  createAnswer: (questionId, data) =>
    api.post(`/quizzes/questions/${questionId}/answers/`, data),

  updateAnswer: (questionId, answerId, data) =>
    api.put(`/quizzes/questions/${questionId}/answers/${answerId}/`, data),

  deleteAnswer: (questionId, answerId) =>
    api.delete(`/quizzes/questions/${questionId}/answers/${answerId}/`),
};

export default quizApi;
