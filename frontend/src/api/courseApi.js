import api from './axiosConfig';

const courseApi = {
  // Courses
  getCourses: (params = {}) =>
    api.get('/courses/', { params }),

  getCourseDetail: (courseId) =>
    api.get(`/courses/${courseId}/`),

  createCourse: (data) =>
    api.post('/courses/', data),

  updateCourse: (courseId, data) =>
    api.patch(`/courses/${courseId}/`, data),

  deleteCourse: (courseId) =>
    api.delete(`/courses/${courseId}/`),

  publishCourse: (courseId) =>
    api.post(`/courses/${courseId}/publish/`),

  duplicateCourse: (courseId) =>
    api.post(`/courses/${courseId}/duplicate/`),

  getCourseStudents: (courseId) =>
    api.get(`/courses/${courseId}/students/`),

  // Categories
  getCategories: () =>
    api.get('/courses/categories/'),

  // Sections
  getCourseSections: (courseId) =>
    api.get(`/courses/${courseId}/sections/`),

  createSection: (courseId, data) =>
    api.post(`/courses/${courseId}/sections/`, data),

  updateSection: (courseId, sectionId, data) =>
    api.patch(`/courses/${courseId}/sections/${sectionId}/`, data),

  deleteSection: (courseId, sectionId) =>
    api.delete(`/courses/${courseId}/sections/${sectionId}/`),

  // Lessons
  getSectionLessons: (courseId, sectionId) =>
    api.get(`/courses/${courseId}/sections/${sectionId}/lessons/`),

  createLesson: (courseId, sectionId, data) =>
    api.post(`/courses/${courseId}/sections/${sectionId}/lessons/`, data),

  updateLesson: (courseId, sectionId, lessonId, data) =>
    api.patch(`/courses/${courseId}/sections/${sectionId}/lessons/${lessonId}/`, data),

  deleteLesson: (courseId, sectionId, lessonId) =>
    api.delete(`/courses/${courseId}/sections/${sectionId}/lessons/${lessonId}/`),

  // Enrollments
  getMyEnrollments: () =>
    api.get('/courses/enrollments/'),

  enrollInCourse: (courseId) =>
    api.post('/courses/enrollments/', { course: courseId }),

  unenroll: (enrollmentId) =>
    api.delete(`/courses/enrollments/${enrollmentId}/`),
};

export default courseApi;
