import React from 'react';
import { Link } from 'react-router-dom';
import { formatDuration, formatPrice } from '../../utils/formatters';

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '24px',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: '12px',
    border: '1px solid #e2e8f0',
    overflow: 'hidden',
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'pointer',
    textDecoration: 'none',
    color: 'inherit',
    display: 'block',
  },
  thumbnail: {
    width: '100%',
    height: '180px',
    objectFit: 'cover',
    backgroundColor: '#e2e8f0',
  },
  thumbnailPlaceholder: {
    width: '100%',
    height: '180px',
    backgroundColor: '#e2e8f0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#94a3b8',
    fontSize: '40px',
  },
  content: {
    padding: '16px 20px',
  },
  category: {
    fontSize: '12px',
    fontWeight: 600,
    color: '#3B82F6',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: '8px',
  },
  title: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#1e293b',
    marginBottom: '8px',
    lineHeight: 1.4,
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  instructor: {
    fontSize: '13px',
    color: '#64748b',
    marginBottom: '12px',
  },
  meta: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    fontSize: '13px',
    color: '#64748b',
  },
  rating: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    color: '#f59e0b',
    fontWeight: 600,
  },
  price: {
    fontSize: '18px',
    fontWeight: 700,
    color: '#1e293b',
  },
  priceFree: {
    fontSize: '18px',
    fontWeight: 700,
    color: '#10b981',
  },
  stats: {
    display: 'flex',
    gap: '16px',
    fontSize: '12px',
    color: '#94a3b8',
    marginTop: '8px',
  },
  level: {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: 600,
    backgroundColor: '#eff6ff',
    color: '#3B82F6',
  },
};

const renderStars = (rating) => {
  const full = Math.floor(rating);
  const hasHalf = rating - full >= 0.5;
  let stars = '';
  for (let i = 0; i < full; i++) stars += '\u2605';
  if (hasHalf) stars += '\u00BD';
  return stars;
};

const CourseList = ({ courses = [], loading = false }) => {
  if (loading) {
    return (
      <div style={styles.grid}>
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} style={{ ...styles.card, opacity: 0.5 }}>
            <div style={styles.thumbnailPlaceholder}>...</div>
            <div style={styles.content}>
              <div style={{ height: '20px', backgroundColor: '#e2e8f0', borderRadius: '4px', marginBottom: '8px' }} />
              <div style={{ height: '14px', backgroundColor: '#e2e8f0', borderRadius: '4px', width: '60%' }} />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (courses.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
        <p style={{ fontSize: '18px', marginBottom: '8px' }}>No courses found</p>
        <p style={{ fontSize: '14px' }}>Try adjusting your filters or search query.</p>
      </div>
    );
  }

  return (
    <div style={styles.grid}>
      {courses.map((course) => (
        <Link key={course.id} to={`/courses/${course.id}`} style={styles.card}>
          {course.thumbnail ? (
            <img src={course.thumbnail} alt={course.title} style={styles.thumbnail} />
          ) : (
            <div style={styles.thumbnailPlaceholder}>{'\u{1F4DA}'}</div>
          )}
          <div style={styles.content}>
            {course.category_name && (
              <div style={styles.category}>{course.category_name}</div>
            )}
            <h3 style={styles.title}>{course.title}</h3>
            <p style={styles.instructor}>{course.instructor_name}</p>
            <div style={styles.meta}>
              <div style={styles.rating}>
                {renderStars(course.average_rating)} {Number(course.average_rating).toFixed(1)}
                <span style={{ color: '#94a3b8', fontWeight: 400 }}>
                  ({course.total_reviews})
                </span>
              </div>
              <span style={course.is_free ? styles.priceFree : styles.price}>
                {course.is_free ? 'Free' : formatPrice(course.price)}
              </span>
            </div>
            <div style={styles.stats}>
              <span>{course.total_lessons} lessons</span>
              <span>{course.total_enrollments} students</span>
              <span style={styles.level}>{course.level}</span>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
};

export default CourseList;
