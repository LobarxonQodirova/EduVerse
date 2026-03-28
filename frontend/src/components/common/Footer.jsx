import React from 'react';

const styles = {
  footer: {
    padding: '24px 32px',
    backgroundColor: '#ffffff',
    borderTop: '1px solid #e2e8f0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '16px',
    fontSize: '13px',
    color: '#64748b',
  },
  links: {
    display: 'flex',
    gap: '24px',
  },
  link: {
    color: '#64748b',
    textDecoration: 'none',
    transition: 'color 0.2s',
  },
  brand: {
    fontWeight: 600,
    color: '#3B82F6',
  },
};

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer style={styles.footer}>
      <div>
        <span style={styles.brand}>EduVerse</span> {currentYear}. All rights reserved.
      </div>
      <div style={styles.links}>
        <a href="/about" style={styles.link}>About</a>
        <a href="/privacy" style={styles.link}>Privacy</a>
        <a href="/terms" style={styles.link}>Terms</a>
        <a href="/help" style={styles.link}>Help Center</a>
        <a href="/contact" style={styles.link}>Contact</a>
      </div>
    </footer>
  );
};

export default Footer;
