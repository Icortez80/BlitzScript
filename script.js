
const TRACK_URL = 'NFLTheme.mp3';
const TRACK_NAME = 'GAME TIME BABY!';

const audio = new Audio(TRACK_URL);
audio.loop = true;
audio.volume = 0.5;

let isPlaying = false;

const playBtn    = document.getElementById('play-btn');
const trackName  = document.querySelector('.track-name');
const trackStatus = document.querySelector('.track-status');
const volSlider  = document.getElementById('volume-slider');

if (trackName) trackName.textContent = TRACK_NAME;

function setPlayState(playing) {
  isPlaying = playing;
  if (playBtn) {
    playBtn.textContent = playing ? '⏸' : '▶';
    playBtn.setAttribute('aria-label', playing ? 'Pause' : 'Play');
  }
  if (trackStatus) trackStatus.textContent = playing ? 'Now Playing' : 'Paused';
}

if (playBtn) {
  playBtn.addEventListener('click', () => {
    if (isPlaying) {
      audio.pause();
      setPlayState(false);
    } else {
      audio.play().catch(() => {
        /* Browser blocked autoplay — user gesture already happened here,
           so this catch is just a safety net */
      });
      setPlayState(true);
    }
  });
}

if (volSlider) {
  volSlider.value = audio.volume * 100;
  volSlider.addEventListener('input', () => {
    audio.volume = volSlider.value / 100;
  });
}

/* Optional: attempt autoplay on load (browsers may block this).
   If blocked, the player sits ready for the user to press play. */
window.addEventListener('load', () => {
  audio.play()
    .then(() => setPlayState(true))
    .catch(() => setPlayState(false)); // silently fail — user will click play
});

/* ─────────────────────────────────────────
   SCROLL FADE-IN
   Adds .visible to elements as they enter
   the viewport for entrance animations
───────────────────────────────────────── */
const fadeEls = document.querySelectorAll('section, aside');

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.1 }
);

fadeEls.forEach(el => {
  el.style.animationPlayState = 'paused';
  observer.observe(el);
});