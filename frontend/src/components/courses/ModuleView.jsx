import React, { useState } from 'react';
import { formatDuration } from '../../utils/formatters';

const styles = {
  module: {
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    marginBottom: '8px',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px 20px',
    backgroundColor: '#f8fafc',
    cursor: 'pointer',
    userSelect: 'none',
    transition: 'background-color 0.2s',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  arrow: {
    fontSize: '12px',
    color: '#64748b',
    transition: 'transform 0.2s',
  },
  title: {
    fontSize: '15px',
    fontWeight: 600,
    color: '#1e293b',
  },
  meta: {
    fontSize: '13px',
    color: '#64748b',
  },
  lessonList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  lesson: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 20px 12px 48px',
    borderTop: '1px solid #f1f5f9',
    fontSize: '14px',
    color: '#475569',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  lessonLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  lessonIcon: {
    width: '24px',
    height: '24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '14px',
  },
  lessonTitle: {
    fontSize: '14px',
    color: '#334155',
  },
  lessonRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    fontSize: '12px',
    color: '#94a3b8',
  },
  previewBadge: {
    padding: '2px 8px',
    borderRadius: '4px',
    backgroundColor: '#eff6ff',
    color: '#3B82F6',
    fontSize: '11px',
    fontWeight: 600,
  },
};

const contentTypeIcons = {
  video: '\u25B6',
  article: '\u{1F4C4}',
  quiz: '\u2753',
  assignment: '\u{1F4DD}',
  live: '\u{1F534}',
};

const ModuleView = ({ section, onLessonClick }) => {
  const [expanded, setExpanded] = useState(false);

  const lessons = section.lessons || [];

  return (
    <div style={styles.module}>
      <div style={styles.header} onClick={() => setExpanded(!expanded)}>
        <div style={styles.headerLeft}>
          <span style={{ ...styles.arrow, transform: expanded ? 'rotate(90deg)' : 'none' }}>
            {'\u25B6'}
          </span>
          <span style={styles.title}>{section.title}</span>
        </div>
        <span style={styles.meta}>
          {lessons.length} lesson{lessons.length !== 1 ? 's' : ''}
        </span>
      </div>

      {expanded && (
        <ul style={styles.lessonList}>
          {lessons.map((lesson) => (
            <li
              key={lesson.id}
              style={styles.lesson}
              onClick={() => onLessonClick?.(lesson)}
            >
              <div style={styles.lessonLeft}>
                <span style={styles.lessonIcon}>
                  {contentTypeIcons[lesson.content_type] || '\u{1F4C4}'}
                </span>
                <span style={styles.lessonTitle}>{lesson.title}</span>
              </div>
              <div style={styles.lessonRight}>
                {lesson.is_preview && (
                  <span style={styles.previewBadge}>Preview</span>
                )}
                {lesson.duration && (
                  <span>{formatDuration(lesson.duration)}</span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ModuleView;
