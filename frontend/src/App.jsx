import React, { useState, useEffect } from 'react';

const API_BASE = "/api";

export default function App() {
  const [view, setView] = useState('login'); // login, interests, generate, library
  const [user, setUser] = useState('');
  const [subjects, setSubjects] = useState([]);
  const [podcasts, setPodcasts] = useState([]);

  // 1. LOGIN PAGE
  if (view === 'login') return (
    <div style={{ padding: 40 }}>
      <h1>Podcast Login</h1>
      <input id="uname" placeholder="Username" />
      <button onClick={async () => {
        const name = document.getElementById('uname').value;
        await fetch(`${API_BASE}/login?username=${name}`, { method: 'POST' });
        setUser(name);
        setView('interests');
      }}>Enter</button>
    </div>
  );

  // 2. INTERESTS PAGE
  if (view === 'interests') return (
    <div style={{ padding: 40 }}>
      <h1>Your Interests</h1>
      <button onClick={() => setView('generate')}>Continue to Generate</button>
    </div>
  );

  // 3. GENERATE PAGE
  if (view === 'generate') return (
    <div style={{ padding: 40 }}>
      <h1>Generate Podcast</h1>
      <button onClick={async () => {
        const res = await fetch(`${API_BASE}/subjects?username=${user}`);
        const data = await res.json();
        setSubjects(data.subjects || []);
      }}>Find New Topics</button>
      <ul>
        {subjects.map(s => (
          <li key={s}>{s} <button onClick={() => alert("Generating...")}>Generate</button></li>
        ))}
      </ul>
      <button onClick={() => setView('library')}>View My Library</button>
    </div>
  );

  // 4. LIBRARY PAGE
  if (view === 'library') return (
    <div style={{ padding: 40 }}>
      <h1>My Podcasts</h1>
      <button onClick={async () => {
        const res = await fetch(`${API_BASE}/my-podcasts?username=${user}`);
        const data = await res.json();
        setPodcasts(data.podcasts);
      }}>Refresh Library</button>
      <ul>
        {podcasts.map(p => <li key={p}>{p}</li>)}
      </ul>
      <button onClick={() => setView('generate')}>Back</button>
    </div>
  );
}