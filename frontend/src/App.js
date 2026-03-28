import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import Footer from './components/common/Footer';
import DashboardPage from './pages/DashboardPage';
import CoursesPage from './pages/CoursesPage';
import CourseDetailPage from './pages/CourseDetailPage';
import AssignmentsPage from './pages/AssignmentsPage';
import GradesPage from './pages/GradesPage';
import CalendarPage from './pages/CalendarPage';
import DiscussionsPage from './pages/DiscussionsPage';

const ProtectedRoute = ({ children }) => {
  const { user, token } = useSelector((state) => state.auth);
  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const appStyles = {
  display: 'flex',
  minHeight: '100vh',
  backgroundColor: '#f8fafc',
};

const mainContent = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  marginLeft: '260px',
  transition: 'margin-left 0.3s ease',
};

const pageContainer = {
  flex: 1,
  padding: '24px 32px',
  maxWidth: '1400px',
  width: '100%',
};

function App() {
  const { token } = useSelector((state) => state.auth);

  if (!token) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
        <Navbar />
        <Routes>
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/courses/:courseId" element={<CourseDetailPage />} />
          <Route path="*" element={<CoursesPage />} />
        </Routes>
        <Footer />
      </div>
    );
  }

  return (
    <div style={appStyles}>
      <Sidebar />
      <div style={mainContent}>
        <Navbar />
        <div style={pageContainer}>
          <Routes>
            <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/courses" element={<ProtectedRoute><CoursesPage /></ProtectedRoute>} />
            <Route path="/courses/:courseId" element={<ProtectedRoute><CourseDetailPage /></ProtectedRoute>} />
            <Route path="/assignments" element={<ProtectedRoute><AssignmentsPage /></ProtectedRoute>} />
            <Route path="/grades" element={<ProtectedRoute><GradesPage /></ProtectedRoute>} />
            <Route path="/calendar" element={<ProtectedRoute><CalendarPage /></ProtectedRoute>} />
            <Route path="/discussions" element={<ProtectedRoute><DiscussionsPage /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </div>
  );
}

export default App;
