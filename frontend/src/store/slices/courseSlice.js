import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import courseApi from '../../api/courseApi';

export const fetchCourses = createAsyncThunk(
  'courses/fetchCourses',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await courseApi.getCourses(params);
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch courses.');
    }
  }
);

export const fetchCourseDetail = createAsyncThunk(
  'courses/fetchCourseDetail',
  async (courseId, { rejectWithValue }) => {
    try {
      const response = await courseApi.getCourseDetail(courseId);
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch course details.');
    }
  }
);

export const fetchCategories = createAsyncThunk(
  'courses/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await courseApi.getCategories();
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch categories.');
    }
  }
);

export const fetchMyEnrollments = createAsyncThunk(
  'courses/fetchMyEnrollments',
  async (_, { rejectWithValue }) => {
    try {
      const response = await courseApi.getMyEnrollments();
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch enrollments.');
    }
  }
);

export const enrollInCourse = createAsyncThunk(
  'courses/enrollInCourse',
  async (courseId, { rejectWithValue }) => {
    try {
      const response = await courseApi.enrollInCourse(courseId);
      return response.data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.error || 'Failed to enroll in course.'
      );
    }
  }
);

const initialState = {
  courses: [],
  currentCourse: null,
  categories: [],
  enrollments: [],
  loading: false,
  error: null,
  pagination: {
    count: 0,
    next: null,
    previous: null,
  },
};

const courseSlice = createSlice({
  name: 'courses',
  initialState,
  reducers: {
    clearCurrentCourse: (state) => {
      state.currentCourse = null;
    },
    clearCourseError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch courses
      .addCase(fetchCourses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCourses.fulfilled, (state, action) => {
        state.loading = false;
        state.courses = action.payload.results || action.payload;
        state.pagination = {
          count: action.payload.count || 0,
          next: action.payload.next,
          previous: action.payload.previous,
        };
      })
      .addCase(fetchCourses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch course detail
      .addCase(fetchCourseDetail.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchCourseDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.currentCourse = action.payload;
      })
      .addCase(fetchCourseDetail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Categories
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload.results || action.payload;
      })
      // Enrollments
      .addCase(fetchMyEnrollments.fulfilled, (state, action) => {
        state.enrollments = action.payload.results || action.payload;
      })
      // Enroll
      .addCase(enrollInCourse.fulfilled, (state, action) => {
        state.enrollments.push(action.payload);
        if (state.currentCourse) {
          state.currentCourse.is_enrolled = true;
          state.currentCourse.total_enrollments += 1;
        }
      })
      .addCase(enrollInCourse.rejected, (state, action) => {
        state.error = action.payload;
      });
  },
});

export const { clearCurrentCourse, clearCourseError } = courseSlice.actions;
export default courseSlice.reducer;
