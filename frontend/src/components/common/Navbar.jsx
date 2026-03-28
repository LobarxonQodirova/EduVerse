import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logout } from '../../store/slices/authSlice';

const styles = {
  nav: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 32px',
    height: '64px',
    backgroundColor: '#ffffff',
    borderBottom: '1px solid #e2e8f0',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  logo: {
    fontSize: '22px',
    fontWeight: 700,
    color: '#3B82F6',
    textDecoration: 'none',
    letterSpacing: '-0.5px',
  },
  logoAccent: {
    color: '#1e293b',
  },
  searchBar: {
    flex: 1,
    maxWidth: '480px',
    margin: '0 32px',
  },
  searchInput: {
    width: '100%',
    padding: '10px 16px',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    fontSize: '14px',
    outline: 'none',
    backgroundColor: '#f8fafc',
    transition: 'border-color 0.2s',
  },
  rightSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    cursor: 'pointer',
    position: 'relative',
  },
  avatar: {
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    backgroundColor: '#3B82F6',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
    fontWeight: 600,
  },
  userName: {
    fontSize: '14px',
    fontWeight: 500,
    color: '#334155',
  },
  dropdown: {
    position: 'absolute',
    top: '48px',
    right: 0,
    backgroundColor: '#fff',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '8px 0',
    minWidth: '180px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    zIndex: 200,
  },
  dropdownItem: {
    padding: '10px 16px',
    fontSize: '14px',
    color: '#334155',
    cursor: 'pointer',
    textDecoration: 'none',
    display: 'block',
    border: 'none',
    background: 'none',
    width: '100%',
    textAlign: 'left',
  },
  authLinks: {
    display: 'flex',
    gap: '12px',
  },
  loginBtn: {
    padding: '8px 20px',
    border: '1px solid #3B82F6',
    borderRadius: '6px',
    color: '#3B82F6',
    backgroundColor: 'transparent',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 500,
  },
  signupBtn: {
    padding: '8px 20px',
    border: 'none',
    borderRadius: '6px',
    color: '#fff',
    backgroundColor: '#3B82F6',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 500,
  },
};

const Navbar = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const [showDropdown, setShowDropdown] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleLogout = () => {
    dispatch(logout());
    navigate('/');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/courses?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  const getInitials = (name) => {
    if (!name) return '?';
    return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <nav style={styles.nav}>
      <Link to="/" style={styles.logo}>
        Edu<span style={styles.logoAccent}>Verse</span>
      </Link>

      <form style={styles.searchBar} onSubmit={handleSearch}>
        <input
          style={styles.searchInput}
          type="text"
          placeholder="Search courses, topics, instructors..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </form>

      <div style={styles.rightSection}>
        {user ? (
          <div style={styles.userInfo} onClick={() => setShowDropdown(!showDropdown)}>
            <div style={styles.avatar}>
              {getInitials(user.full_name || user.email)}
            </div>
            <span style={styles.userName}>
              {user.first_name || user.email}
            </span>

            {showDropdown && (
              <div style={styles.dropdown}>
                <Link to="/dashboard" style={styles.dropdownItem}>Dashboard</Link>
                <Link to="/courses" style={styles.dropdownItem}>My Courses</Link>
                <Link to="/grades" style={styles.dropdownItem}>Grades</Link>
                <hr style={{ margin: '4px 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />
                <button onClick={handleLogout} style={styles.dropdownItem}>
                  Sign Out
                </button>
              </div>
            )}
          </div>
        ) : (
          <div style={styles.authLinks}>
            <button style={styles.loginBtn}>Log In</button>
            <button style={styles.signupBtn}>Sign Up</button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
