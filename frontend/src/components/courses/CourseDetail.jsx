import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { enrollInCourse } from '../../store/slices/courseSlice';
import ModuleView from './ModuleView';
import { formatPrice } from '../../utils/formatters';

const styles = {
  hero: {
    background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
    color: '#fff',
    padding: '48px 32px',
    borderRadius: '16px',
    marginBottom: '32px',
  },
  heroTitle: {
    fontSize: '32px',
    fontWeight: 700,
    marginBottom: '12px',
    lineHeight: 1.3,
  },
  heroSubtitle: {
    fontSize: '18px',
    color: '#cbd5e1',
    marginBottom: '20px',
  },
  heroMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '24px',
    fontSize: '14px',
    color: '#94a3b8',
    flexWrap: 'wrap',
  },
  metaItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  layout: {
    display: 'grid',
    gridTemplateColumns: '1fr 360px',
    gap: '32px',
    alignItems: 'start',
  },
  mainContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: '12px',
    border: '1px solid #e2e8f0',
    padding: '24px',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: 600,
    color: '#1e293b',
    marginBottom: '16px',
  },
  description: {
    fontSize: '15px',
    lineHeight: 1.7,
    color: '#475569',
  },
  learningList: {
    listStyle: 'none',
    padding: 0,
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: '12px',
  },
  learningItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '8px',
    fontSize: '14px',
    color: '#334155',
    lineHeight: 1.5,
  },
  checkmark: {
    color: '#10b981',
    fontWeight: 700,
    marginTop: '2px',
  },
  sideCard: {
    backgroundColor: '#fff',
    borderRadius: '12px',
    border: '1px solid #e2e8f0',
    padding: '24px',
    position: 'sticky',
    top: '88px',
  },
  price: {
    fontSize: '32px',
    fontWeight: 700,
    color: '#1e293b',
    marginBottom: '16px',
  },
  enrollBtn: {
    width: '100%',
    padding: '14px',
    backgroundColor: '#3B82F6',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    marginBottom: '16px',
    transition: 'background-color 0.2s',
  },
  enrolledBadge: {
    width: '100%',
    padding: '14px',
    backgroundColor: '#10b981',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 600,
    textAlign: 'center',
    marginBottom: '16px',
  },
  courseInfo: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  courseInfoItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '10px 0',
    borderBottom: '1px solid #f1f5f9',
    fontSize: '14px',
    color: '#475569',
  },
  instructorCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '16px',
    backgroundColor: '#f8fafc',
    borderRadius: '8px',
  },
  instructorAvatar: {
    width: '56px',
    height: '56px',
    borderRadius: '50%',
    backgroundColor: '#3B82F6',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '20px',
    fontWeight: 600,
  },
};

const CourseDetail = ({ course }) => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  if (!course) return null;

  const handleEnroll = () => {
    dispatch(enrollInCourse(course.id));
  };

  const instructorName =
    course.instructor_detail?.full_name || course.instructor_detail?.email || 'Instructor';

  return (
    <div>
      <div style={styles.hero}>
        <h1 style={styles.heroTitle}>{course.title}</h1>
        {course.subtitle && <p style={styles.heroSubtitle}>{course.subtitle}</p>}
        <div style={styles.heroMeta}>
          <span style={styles.metaItem}>By {instructorName}</span>
          <span style={styles.metaItem}>
            {'\u2605'} {Number(course.average_rating).toFixed(1)} ({course.total_reviews} reviews)
          </span>
          <span style={styles.metaItem}>{course.total_enrollments} students</span>
          <span style={styles.metaItem}>{course.level}</span>
          <span style={styles.metaItem}>{course.language?.toUpperCase()}</span>
        </div>
      </div>

      <div style={styles.layout}>
        <div style={styles.mainContent}>
          {course.what_you_will_learn?.length > 0 && (
            <div style={styles.section}>
              <h2 style={styles.sectionTitle}>What You Will Learn</h2>
              <ul style={styles.learningList}>
                {course.what_you_will_learn.map((item, idx) => (
                  <li key={idx} style={styles.learningItem}>
                    <span style={styles.checkmark}>{'\u2713'}</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>Description</h2>
            <div style={styles.description}>{course.description}</div>
          </div>

          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>
              Course Content ({course.sections?.length || 0} sections, {course.total_lessons} lessons)
            </h2>
            {course.sections?.map((section) => (
              <ModuleView key={section.id} section={section} />
            ))}
          </div>

          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>Instructor</h2>
            <div style={styles.instructorCard}>
              <div style={styles.instructorAvatar}>
                {instructorName.charAt(0).toUpperCase()}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '16px', color: '#1e293b' }}>
                  {instructorName}
                </div>
                <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
                  {course.instructor_detail?.email}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style={styles.sideCard}>
          <div style={styles.price}>
            {course.is_free ? 'Free' : formatPrice(course.price)}
          </div>

          {course.is_enrolled ? (
            <div style={styles.enrolledBadge}>{'\u2713'} Enrolled</div>
          ) : (
            user?.role === 'student' && (
              <button style={styles.enrollBtn} onClick={handleEnroll}>
                {course.is_free ? 'Enroll for Free' : 'Enroll Now'}
              </button>
            )
          )}

          <ul style={styles.courseInfo}>
            <li style={styles.courseInfoItem}>
              <span>Lessons</span><span>{course.total_lessons}</span>
            </li>
            <li style={styles.courseInfoItem}>
              <span>Level</span><span>{course.level}</span>
            </li>
            <li style={styles.courseInfoItem}>
              <span>Language</span><span>{course.language?.toUpperCase()}</span>
            </li>
            <li style={styles.courseInfoItem}>
              <span>Students</span><span>{course.total_enrollments}</span>
            </li>
            <li style={styles.courseInfoItem}>
              <span>Sections</span><span>{course.sections?.length || 0}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;
