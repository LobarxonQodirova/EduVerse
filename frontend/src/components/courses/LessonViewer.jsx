import React, { useEffect, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import VideoPlayer from '../common/VideoPlayer';
import { completeLesson } from '../../store/slices/progressSlice';

const styles = {
  container: {
    display: 'grid',
    gridTemplateColumns: '1fr 320px',
    gap: '24px',
    minHeight: '600px',
  },
  mainArea: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  lessonHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 0',
    borderBottom: '1px solid #e2e8f0',
  },
  lessonTitle: {
    fontSize: '22px',
    fontWeight: 600,
    color: '#1e293b',
  },
  lessonType: {
    padding: '4px 12px',
    borderRadius: '6px',
    fontSize: '12px',
    fontWeight: 600,
    backgroundColor: '#eff6ff',
    color: '#3B82F6',
    textTransform: 'capitalize',
  },
  articleContent: {
    backgroundColor: '#fff',
    borderRadius: '12px',
    border: '1px solid #e2e8f0',
    padding: '32px',
    fontSize: '15px',
    lineHeight: 1.8,
    color: '#334155',
  },
  completeBtn: {
    padding: '12px 24px',
    backgroundColor: '#10b981',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    alignSelf: 'flex-start',
  },
  completedBtn: {
    padding: '12px 24px',
    backgroundColor: '#d1fae5',
    color: '#065f46',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 600,
    alignSelf: 'flex-start',
  },
  sidebar: {
    backgroundColor: '#fff',
    borderRadius: '12px',
    border: '1px solid #e2e8f0',
    padding: '20px',
    maxHeight: '600px',
    overflowY: 'auto',
  },
  sidebarTitle: {
    fontSize: '16px',
    fontWeight: 600,
    color: '#1e293b',
    marginBottom: '16px',
  },
  lessonNav: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  lessonNavItem: {
    padding: '10px 12px',
    borderRadius: '6px',
    fontSize: '13px',
    color: '#475569',
    cursor: 'pointer',
    marginBottom: '4px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    transition: 'background-color 0.2s',
  },
  activeLesson: {
    backgroundColor: '#eff6ff',
    color: '#3B82F6',
    fontWeight: 600,
  },
  resources: {
    marginTop: '24px',
    padding: '16px',
    backgroundColor: '#f8fafc',
    borderRadius: '8px',
  },
  resourceTitle: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#1e293b',
    marginBottom: '12px',
  },
  resourceLink: {
    display: 'block',
    padding: '6px 0',
    fontSize: '13px',
    color: '#3B82F6',
    textDecoration: 'none',
  },
};

const LessonViewer = ({ lesson, content, allLessons = [], onNavigate, courseId, isCompleted }) => {
  const dispatch = useDispatch();

  const handleComplete = useCallback(() => {
    if (lesson && courseId) {
      dispatch(completeLesson({
        lessonId: lesson.id,
        courseId,
        timeSpent: lesson.duration || null,
      }));
    }
  }, [dispatch, lesson, courseId]);

  const handleVideoComplete = useCallback(() => {
    handleComplete();
  }, [handleComplete]);

  if (!lesson) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
        <p style={{ fontSize: '16px' }}>Select a lesson to begin learning.</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.mainArea}>
        <div style={styles.lessonHeader}>
          <h2 style={styles.lessonTitle}>{lesson.title}</h2>
          <span style={styles.lessonType}>{lesson.content_type}</span>
        </div>

        {lesson.content_type === 'video' && content?.video_url && (
          <VideoPlayer
            url={content.video_url}
            onComplete={handleVideoComplete}
            title={lesson.title}
          />
        )}

        {lesson.content_type === 'article' && content?.article_body && (
          <div style={styles.articleContent}>
            {content.article_body}
          </div>
        )}

        {lesson.description && (
          <div style={{ fontSize: '14px', color: '#64748b', lineHeight: 1.6 }}>
            {lesson.description}
          </div>
        )}

        {isCompleted ? (
          <button style={styles.completedBtn}>{'\u2713'} Completed</button>
        ) : (
          <button style={styles.completeBtn} onClick={handleComplete}>
            Mark as Complete
          </button>
        )}

        {content?.external_resources?.length > 0 && (
          <div style={styles.resources}>
            <h4 style={styles.resourceTitle}>Additional Resources</h4>
            {content.external_resources.map((res, idx) => (
              <a key={idx} href={res.url} style={styles.resourceLink} target="_blank" rel="noopener noreferrer">
                {res.title}
              </a>
            ))}
          </div>
        )}
      </div>

      <div style={styles.sidebar}>
        <h3 style={styles.sidebarTitle}>Lessons</h3>
        <ul style={styles.lessonNav}>
          {allLessons.map((l) => (
            <li
              key={l.id}
              style={{
                ...styles.lessonNavItem,
                ...(l.id === lesson.id ? styles.activeLesson : {}),
              }}
              onClick={() => onNavigate?.(l)}
            >
              <span>{l.content_type === 'video' ? '\u25B6' : '\u{1F4C4}'}</span>
              {l.title}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default LessonViewer;
