import React from 'react';
import { NavLink } from 'react-router-dom';
import { useSelector } from 'react-redux';

const styles = {
  sidebar: {
    width: '260px',
    height: '100vh',
    position: 'fixed',
    left: 0,
    top: 0,
    backgroundColor: '#1e293b',
    color: '#e2e8f0',
    display: 'flex',
    flexDirection: 'column',
    paddingTop: '24px',
    zIndex: 50,
    overflowY: 'auto',
  },
  logo: {
    fontSize: '24px',
    fontWeight: 700,
    color: '#3B82F6',
    padding: '0 24px 32px',
    letterSpacing: '-0.5px',
  },
  logoAccent: {
    color: '#f1f5f9',
  },
  section: {
    marginBottom: '24px',
  },
  sectionTitle: {
    fontSize: '11px',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '1px',
    color: '#64748b',
    padding: '0 24px 8px',
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    padding: '12px 24px',
    color: '#94a3b8',
    textDecoration: 'none',
    fontSize: '14px',
    fontWeight: 500,
    transition: 'all 0.2s',
    borderLeft: '3px solid transparent',
    gap: '12px',
  },
  navItemActive: {
    color: '#f1f5f9',
    backgroundColor: 'rgba(59, 130, 246, 0.15)',
    borderLeftColor: '#3B82F6',
  },
  icon: {
    fontSize: '18px',
    width: '20px',
    textAlign: 'center',
  },
  progressSection: {
    padding: '16px 24px',
    marginTop: 'auto',
    borderTop: '1px solid #334155',
  },
  progressLabel: {
    fontSize: '12px',
    color: '#64748b',
    marginBottom: '8px',
  },
  progressBar: {
    height: '6px',
    backgroundColor: '#334155',
    borderRadius: '3px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3B82F6',
    borderRadius: '3px',
    transition: 'width 0.3s ease',
  },
};

const studentNav = [
  { path: '/dashboard', label: 'Dashboard', icon: '\u2302' },
  { path: '/courses', label: 'My Courses', icon: '\u{1F4DA}' },
  { path: '/assignments', label: 'Assignments', icon: '\u{1F4DD}' },
  { path: '/grades', label: 'Grades', icon: '\u{1F4CA}' },
  { path: '/discussions', label: 'Discussions', icon: '\u{1F4AC}' },
  { path: '/calendar', label: 'Calendar', icon: '\u{1F4C5}' },
];

const instructorNav = [
  { path: '/dashboard', label: 'Dashboard', icon: '\u2302' },
  { path: '/courses', label: 'Courses', icon: '\u{1F4DA}' },
  { path: '/assignments', label: 'Assignments', icon: '\u{1F4DD}' },
  { path: '/grades', label: 'Gradebook', icon: '\u{1F4CA}' },
  { path: '/discussions', label: 'Discussions', icon: '\u{1F4AC}' },
  { path: '/calendar', label: 'Calendar', icon: '\u{1F4C5}' },
];

const Sidebar = () => {
  const { user } = useSelector((state) => state.auth);
  const { dashboardStats } = useSelector((state) => state.progress);

  const navItems = user?.role === 'instructor' ? instructorNav : studentNav;
  const overallProgress = dashboardStats
    ? Math.round(
        (dashboardStats.total_completed / Math.max(dashboardStats.total_enrolled, 1)) * 100
      )
    : 0;

  return (
    <aside style={styles.sidebar}>
      <div style={styles.logo}>
        Edu<span style={styles.logoAccent}>Verse</span>
      </div>

      <div style={styles.section}>
        <div style={styles.sectionTitle}>Main Menu</div>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            style={({ isActive }) => ({
              ...styles.navItem,
              ...(isActive ? styles.navItemActive : {}),
            })}
          >
            <span style={styles.icon}>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </div>

      {user?.role === 'student' && (
        <div style={styles.progressSection}>
          <div style={styles.progressLabel}>
            Overall Progress: {overallProgress}%
          </div>
          <div style={styles.progressBar}>
            <div
              style={{ ...styles.progressFill, width: `${overallProgress}%` }}
            />
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
