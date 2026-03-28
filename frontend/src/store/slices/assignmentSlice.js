import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import assignmentApi from '../../api/assignmentApi';

export const fetchAssignments = createAsyncThunk(
  'assignments/fetchAssignments',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await assignmentApi.getAssignments(params);
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch assignments.');
    }
  }
);

export const fetchAssignmentDetail = createAsyncThunk(
  'assignments/fetchAssignmentDetail',
  async (assignmentId, { rejectWithValue }) => {
    try {
      const response = await assignmentApi.getAssignmentDetail(assignmentId);
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch assignment details.');
    }
  }
);

export const submitAssignment = createAsyncThunk(
  'assignments/submitAssignment',
  async (submissionData, { rejectWithValue }) => {
    try {
      const response = await assignmentApi.createSubmission(submissionData);
      return response.data;
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.detail ||
        error.response?.data?.non_field_errors?.[0] ||
        'Failed to submit assignment.'
      );
    }
  }
);

export const fetchMySubmissions = createAsyncThunk(
  'assignments/fetchMySubmissions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await assignmentApi.getMySubmissions();
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to fetch submissions.');
    }
  }
);

export const gradeSubmission = createAsyncThunk(
  'assignments/gradeSubmission',
  async ({ submissionId, gradeData }, { rejectWithValue }) => {
    try {
      const response = await assignmentApi.gradeSubmission(submissionId, gradeData);
      return response.data;
    } catch (error) {
      return rejectWithValue('Failed to grade submission.');
    }
  }
);

const initialState = {
  assignments: [],
  currentAssignment: null,
  submissions: [],
  loading: false,
  submitting: false,
  error: null,
};

const assignmentSlice = createSlice({
  name: 'assignments',
  initialState,
  reducers: {
    clearCurrentAssignment: (state) => {
      state.currentAssignment = null;
    },
    clearAssignmentError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch assignments
      .addCase(fetchAssignments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAssignments.fulfilled, (state, action) => {
        state.loading = false;
        state.assignments = action.payload.results || action.payload;
      })
      .addCase(fetchAssignments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch assignment detail
      .addCase(fetchAssignmentDetail.fulfilled, (state, action) => {
        state.currentAssignment = action.payload;
      })
      // Submit assignment
      .addCase(submitAssignment.pending, (state) => {
        state.submitting = true;
        state.error = null;
      })
      .addCase(submitAssignment.fulfilled, (state, action) => {
        state.submitting = false;
        state.submissions.unshift(action.payload);
      })
      .addCase(submitAssignment.rejected, (state, action) => {
        state.submitting = false;
        state.error = action.payload;
      })
      // Fetch submissions
      .addCase(fetchMySubmissions.fulfilled, (state, action) => {
        state.submissions = action.payload.results || action.payload;
      })
      // Grade submission
      .addCase(gradeSubmission.fulfilled, (state, action) => {
        const idx = state.submissions.findIndex(
          (s) => s.id === action.payload.submission
        );
        if (idx !== -1) {
          state.submissions[idx].grade = action.payload;
          state.submissions[idx].status = 'graded';
        }
      });
  },
});

export const { clearCurrentAssignment, clearAssignmentError } = assignmentSlice.actions;
export default assignmentSlice.reducer;
