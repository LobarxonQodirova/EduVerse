import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api/axiosConfig';

export const fetchMyProgress = createAsyncThunk(
  'progress/fetchMyProgress',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/progress/progress/');
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch progress data.');
    }
  }
);

export const completeLesson = createAsyncThunk(
  'progress/completeLesson',
  async ({ lessonId, courseId, timeSpent }, { rejectWithValue }) => {
    try {
      const response = await api.post('/progress/complete-lesson/', {
        lesson: lessonId,
        course: courseId,
        time_spent: timeSpent,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to mark lesson as complete.');
    }
  }
);

export const fetchMyCertificates = createAsyncThunk(
  'progress/fetchMyCertificates',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/progress/certificates/');
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch certificates.');
    }
  }
);

export const fetchDashboardStats = createAsyncThunk(
  'progress/fetchDashboardStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/analytics/student/dashboard/');
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch dashboard stats.');
    }
  }
);

const initialState = {
  progressRecords: [],
  certificates: [],
  dashboardStats: null,
  loading: false,
  error: null,
};

const progressSlice = createSlice({
  name: 'progress',
  initialState,
  reducers: {
    clearProgressError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch progress
      .addCase(fetchMyProgress.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchMyProgress.fulfilled, (state, action) => {
        state.loading = false;
        state.progressRecords = action.payload.results || action.payload;
      })
      .addCase(fetchMyProgress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Complete lesson
      .addCase(completeLesson.fulfilled, (state, action) => {
        const record = action.payload;
        const idx = state.progressRecords.findIndex(
          (p) => p.course === record.course
        );
        if (idx !== -1) {
          state.progressRecords[idx].completed_lessons += 1;
          const total = state.progressRecords[idx].total_lessons || 1;
          state.progressRecords[idx].progress_percent =
            ((state.progressRecords[idx].completed_lessons / total) * 100).toFixed(1);
        }
      })
      // Certificates
      .addCase(fetchMyCertificates.fulfilled, (state, action) => {
        state.certificates = action.payload.results || action.payload;
      })
      // Dashboard stats
      .addCase(fetchDashboardStats.fulfilled, (state, action) => {
        state.dashboardStats = action.payload;
      });
  },
});

export const { clearProgressError } = progressSlice.actions;
export default progressSlice.reducer;
