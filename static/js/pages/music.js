// music.js

document.addEventListener('DOMContentLoaded', () => {
  const loadBtn = document.getElementById('loadSongs');
  const prevBtn = document.getElementById('prevSong');
  const nextBtn = document.getElementById('nextSong');
  const stopBtn = document.getElementById('stopSong');
  const downloadBtn = document.getElementById('downloadSong');
  const player = document.getElementById('player');
  const playlist = document.getElementById('playlist');
  const nowPlaying = document.getElementById('nowPlaying');

  let songs = [];
  let idx = -1;

  function renderList(){
    playlist.innerHTML = '';
    songs.forEach((s, i) => {
      const li = document.createElement('li');
      li.className = 'list-group-item d-flex justify-content-between align-items-center';
      li.innerHTML = `<span>${s.title || 'Untitled'} — <em>${s.artist || 'Unknown'}</em></span>
                      <button class="btn btn-sm btn-outline-primary">Play</button>`;
      li.querySelector('button').addEventListener('click', () => play(i));
      playlist.appendChild(li);
    });
  }

  function setNowPlaying(s){
    nowPlaying.textContent = s ? `${s.title || 'Untitled'} — ${s.artist || 'Unknown'}` : '';
    downloadBtn.href = s ? (s.download_url || s.url) : '#';
    downloadBtn.download = s ? (s.file || 'song.mp3') : '';
  }

  function play(i){
    if(i < 0 || i >= songs.length) return;
    idx = i;
    const s = songs[idx];
    player.src = s.url;
    setNowPlaying(s);
    player.play();
  }

  function prev(){
    if(songs.length === 0) return;
    play((idx - 1 + songs.length) % songs.length);
  }

  function next(){
    if(songs.length === 0) return;
    play((idx + 1) % songs.length);
  }

  async function load(){
    const res = await fetch('/api/random-songs?limit=10');
    const data = await res.json();
    songs = data.items || [];
    renderList();
    if(songs.length) play(0);
  }

  loadBtn && loadBtn.addEventListener('click', load);
  prevBtn && prevBtn.addEventListener('click', prev);
  nextBtn && nextBtn.addEventListener('click', next);
  stopBtn && stopBtn.addEventListener('click', () => player.pause());
  player && player.addEventListener('ended', next);
});
