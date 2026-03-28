import React, { useState, useCallback, useRef } from 'react';
import ReactPlayer from 'react-player';

const styles = {
  wrapper: {
    position: 'relative',
    backgroundColor: '#000',
    borderRadius: '12px',
    overflow: 'hidden',
    aspectRatio: '16 / 9',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    cursor: 'pointer',
    zIndex: 2,
  },
  playButton: {
    width: '72px',
    height: '72px',
    borderRadius: '50%',
    backgroundColor: 'rgba(59, 130, 246, 0.9)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: 'none',
    cursor: 'pointer',
    transition: 'transform 0.2s',
  },
  playIcon: {
    width: 0,
    height: 0,
    borderStyle: 'solid',
    borderWidth: '12px 0 12px 24px',
    borderColor: 'transparent transparent transparent #ffffff',
    marginLeft: '4px',
  },
  controls: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: '12px 16px',
    background: 'linear-gradient(transparent, rgba(0,0,0,0.8))',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    zIndex: 3,
  },
  progressBar: {
    flex: 1,
    height: '4px',
    backgroundColor: 'rgba(255,255,255,0.3)',
    borderRadius: '2px',
    cursor: 'pointer',
    position: 'relative',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3B82F6',
    borderRadius: '2px',
    transition: 'width 0.1s linear',
  },
  timeDisplay: {
    color: '#fff',
    fontSize: '13px',
    fontVariantNumeric: 'tabular-nums',
    minWidth: '80px',
    textAlign: 'center',
  },
  controlBtn: {
    background: 'none',
    border: 'none',
    color: '#fff',
    cursor: 'pointer',
    fontSize: '16px',
    padding: '4px',
  },
};

const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const VideoPlayer = ({ url, onProgress: onProgressCallback, onComplete, title }) => {
  const playerRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [played, setPlayed] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showOverlay, setShowOverlay] = useState(true);
  const [volume, setVolume] = useState(0.8);

  const handlePlay = useCallback(() => {
    setPlaying(true);
    setShowOverlay(false);
  }, []);

  const handlePause = useCallback(() => {
    setPlaying(false);
  }, []);

  const handleProgress = useCallback(
    (state) => {
      setPlayed(state.played);
      if (onProgressCallback) {
        onProgressCallback({
          played: state.played,
          playedSeconds: state.playedSeconds,
          loaded: state.loaded,
        });
      }
    },
    [onProgressCallback]
  );

  const handleEnded = useCallback(() => {
    setPlaying(false);
    if (onComplete) {
      onComplete();
    }
  }, [onComplete]);

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const fraction = (e.clientX - rect.left) / rect.width;
    playerRef.current?.seekTo(fraction, 'fraction');
    setPlayed(fraction);
  };

  if (!url) {
    return (
      <div style={{ ...styles.wrapper, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: '#94a3b8', fontSize: '16px' }}>No video available</p>
      </div>
    );
  }

  return (
    <div style={styles.wrapper}>
      <ReactPlayer
        ref={playerRef}
        url={url}
        playing={playing}
        volume={volume}
        width="100%"
        height="100%"
        onDuration={setDuration}
        onProgress={handleProgress}
        onEnded={handleEnded}
        progressInterval={500}
        style={{ position: 'absolute', top: 0, left: 0 }}
      />

      {showOverlay && (
        <div style={styles.overlay} onClick={handlePlay}>
          <button style={styles.playButton} aria-label="Play video">
            <div style={styles.playIcon} />
          </button>
        </div>
      )}

      <div style={styles.controls}>
        <button style={styles.controlBtn} onClick={playing ? handlePause : handlePlay}>
          {playing ? '\u23F8' : '\u25B6'}
        </button>

        <div style={styles.progressBar} onClick={handleSeek}>
          <div style={{ ...styles.progressFill, width: `${played * 100}%` }} />
        </div>

        <span style={styles.timeDisplay}>
          {formatTime(played * duration)} / {formatTime(duration)}
        </span>

        <button
          style={styles.controlBtn}
          onClick={() => setVolume((v) => (v > 0 ? 0 : 0.8))}
        >
          {volume > 0 ? '\u{1F50A}' : '\u{1F507}'}
        </button>
      </div>
    </div>
  );
};

export default VideoPlayer;
