import api from './axiosConfig';

const assignmentApi = {
  // Assignments
  getAssignments: (params = {}) =>
    api.get('/assignments/assignments/', { params }),

  getAssignmentDetail: (assignmentId) =>
    api.get(`/assignments/assignments/${assignmentId}/`),

  createAssignment: (data) =>
    api.post('/assignments/assignments/', data),

  updateAssignment: (assignmentId, data) =>
    api.patch(`/assignments/assignments/${assignmentId}/`, data),

  deleteAssignment: (assignmentId) =>
    api.delete(`/assignments/assignments/${assignmentId}/`),

  getAssignmentSubmissions: (assignmentId) =>
    api.get(`/assignments/assignments/${assignmentId}/submissions/`),

  // Submissions
  getMySubmissions: () =>
    api.get('/assignments/submissions/'),

  getSubmissionDetail: (submissionId) =>
    api.get(`/assignments/submissions/${submissionId}/`),

  createSubmission: (data) => {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, value);
      }
    });
    return api.post('/assignments/submissions/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Grading
  gradeSubmission: (submissionId, gradeData) =>
    api.post(`/assignments/submissions/${submissionId}/grade/`, gradeData),

  // Feedback
  getSubmissionFeedback: (submissionId) =>
    api.get(`/assignments/submissions/${submissionId}/feedback/`),

  addFeedback: (submissionId, data) =>
    api.post(`/assignments/submissions/${submissionId}/feedback/`, data),
};

export default assignmentApi;
