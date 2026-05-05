import React, { useState, useEffect } from 'react';

const API_BASE = "http://localhost:8000";

export default function App() {
    const [view, setView] = useState('login');
    const [user, setUser] = useState('');
    const [subjects, setSubjects] = useState([]);
    const [podcasts, setPodcasts] = useState([]);
    const handleLogout = () => {
    setUser('');
    setView('login');
    setSubjects([]);
    setPodcasts([]);
    };
    const LogoutButton = () => (
    <button 
        onClick={handleLogout}
        style={{
        position: 'absolute',
        top: '20px',
        right: '20px',
        padding: '8px 15px',
        backgroundColor: '#ff4d4d',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer'
        }}
    >
        Logout
    </button>
    );

  // Fetch the library whenever the "library" view is triggered
  useEffect(() => {
    if (view === 'library' && user) {
      fetch(`${API_BASE}/my-podcasts?username=${user}`)
        .then(res => res.json())
        .then(data => setPodcasts(data.podcasts));
    }
  }, [view, user]);

  // 1. LOGIN PAGE
  if (view === 'login') return (
    <div style={{ padding: 40, fontFamily: 'sans-serif' }}>
      <h1>🎙️ Podcast Login</h1>
      <input id="uname" placeholder="Username" style={{ padding: 10 }} />
      <button onClick={async () => {
        const name = document.getElementById('uname').value;
        if (!name) return alert("Enter a name");
        await fetch(`${API_BASE}/login?username=${name}`, { method: 'POST' });
        setUser(name);
        setView('interests');
      }} style={{ padding: 10, marginLeft: 10 }}>Enter</button>
    </div>
  );

  // 2. INTERESTS PAGE
  if (view === 'interests') return (
    <div style={{ padding: 40, fontFamily: 'sans-serif', position: 'relative' }}>
        <LogoutButton/>
      <h1>Hello, {user}!</h1>
      <p>Set your interests or check your existing episodes.</p>
      <div style={{ display: 'flex', gap: '10px' }}>
        <button onClick={() => setView('generate')} style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px' }}>
          Find New Topics
        </button>
        <button onClick={() => setView('library')} style={{ padding: '10px 20px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '5px' }}>
          View My Library
        </button>
      </div>
    </div>
  );

  // 3. GENERATE PAGE (Topics from Researcher)
  if (view === 'generate') return (
    <div style={{ padding: 40, fontFamily: 'sans-serif', position: 'relative' }}>
      <LogoutButton />
      <h1>Pick a Topic</h1>
      <button onClick={async () => {
        const res = await fetch(`${API_BASE}/subjects?username=${user}`);
        const data = await res.json();
        setSubjects(data.subjects || []);
      }}>Refresh Suggestions</button>
      <ul style={{ marginTop: 20 }}>
        {subjects.map((s, i) => (
          <li key={i} style={{ marginBottom: 15 }}>
            <strong>{s}</strong> <br/>
            <button onClick={() => alert("Backend would trigger Audio class now!")}>Generate Episode</button>
          </li>
        ))}
      </ul>
      <button onClick={() => setView('interests')}>Back</button>
    </div>
  );

  // 4. LIBRARY PAGE (The Podcasts Folder)
  if (view === 'library') return (
    <div style={{ padding: 40, fontFamily: 'sans-serif', position: 'relative' }}>
      <LogoutButton />
      <h1>Your Podcast Library</h1>
      <button onClick={() => setView('interests')} style={{ marginBottom: 20 }}>Back to Interests</button>
      
      {podcasts.length === 0 ? <p>No podcasts found yet. Go generate one!</p> : (
        <div style={{ display: 'grid', gap: '20px' }}>
          {podcasts.map(file => (
            <div key={file} style={{ border: '1px solid #ddd', padding: 15, borderRadius: 8 }}>
              <p style={{ margin: '0 0 10px 0' }}><strong>File:</strong> {file}</p>
              {/* This links to the StaticFiles mount in your FastAPI backend */}
              <audio controls src={`${API_BASE}/audio/${file}`} style={{ width: '100%' }} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}