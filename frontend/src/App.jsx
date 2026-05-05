import React, { useState, useEffect } from 'react';

const API_BASE = "http://localhost:8000";

export default function App() {
    const [view, setView] = useState('login');
    const [user, setUser] = useState('');
    const [subjects, setSubjects] = useState([]);
    const [podcasts, setPodcasts] = useState([]);
    const [interests, setInterests] = useState([]);
    const [newInterest, setNewInterest] = useState('');
    const [generating, setGenerating] = useState(false);
    useEffect(() => {
        const fetchInterests = async () => {
            if (user && view === 'interests') {
                const res = await fetch(`${API_BASE}/login?username=${user}`, { method: 'POST' });
                const data = await res.json();
                setInterests(data.interests || []);
            }
        };
        fetchInterests();
    }, [view, user]);
    useEffect(() => {
        if (view === 'library' && user) {
            fetch(`${API_BASE}/my-podcasts?username=${user}`)
                .then(res => res.json())
                .then(data => setPodcasts(data.podcasts));
        }
    }, [view, user]);
    const handleLogout = () => {
        setUser('');
        setView('login');
        setSubjects([]);
        setPodcasts([]);
        setInterests([]);
    };
    const saveInterests = async (updatedList) => {
        try {
            const response = await fetch(`${API_BASE}/update-interests`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json' 
                },
                // Send username inside the body, not as a query param
                body: JSON.stringify({
                    username: user,
                    interests: updatedList
                })
            });
            
            if (!response.ok) {
                console.error("Failed to save interests:", await response.text());
            }
        } catch (err) {
            console.error("Network error saving interests:", err);
        }
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

    // 1. LOGIN PAGE
    if (view === 'login') return (
        <div style={{ padding: 40, fontFamily: 'sans-serif' }}>
            <h1>🎙️ Podcast Login</h1>
            <input id="uname" placeholder="Username" style={{ padding: 10 }} />
            <button onClick={async () => {
                const name = document.getElementById('uname').value;
                if (!name) return alert("Enter a name");
                
                const res = await fetch(`${API_BASE}/login?username=${name}`, { method: 'POST' });
                const data = await res.json();
                
                setUser(data.username);
                setInterests(data.interests || []);
                setView('interests');   
            }}>Enter</button>
        </div>
    );

    // 2. INTERESTS PAGE
    if (view === 'interests') return (
        <div style={{ padding: 40, fontFamily: 'sans-serif', position: 'relative' }}>
            <LogoutButton />
            <h1>Your Interests, {user}</h1>
            
            <div style={{ marginBottom: '20px' }}>
                <input 
                    value={newInterest}
                    onChange={(e) => setNewInterest(e.target.value)}
                    placeholder="Add an interest (e.g. AI, Space)" 
                    style={{ padding: '10px', width: '250px' }}
                />
                <button onClick={() => {
                    if (!newInterest) return;
                    const updated = [...interests, newInterest];
                    setInterests(updated);
                    saveInterests(updated);
                    setNewInterest('');
                }} style={{ padding: '10px', marginLeft: '10px' }}>Add</button>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '30px' }}>
                {interests.map((item, index) => (
                    <div key={index} style={{ 
                        background: '#e0e0e0', 
                        padding: '5px 15px', 
                        borderRadius: '20px',
                        display: 'flex',
                        alignItems: 'center'
                    }}>
                        {item}
                        <button onClick={() => {
                            const updated = interests.filter((_, i) => i !== index);
                            setInterests(updated);
                            saveInterests(updated);
                        }} style={{ marginLeft: '10px', border: 'none', cursor: 'pointer', color: 'red' }}>x</button>
                    </div>
                ))}
            </div>

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

    // 3. GENERATE PAGE
    // Inside View 3: GENERATE PAGE
    if (view === 'generate') return (
    <div style={{ padding: 40, fontFamily: 'sans-serif', position: 'relative' }}>
        <LogoutButton />
        <h1>Pick a Topic</h1>
        
        <button onClick={async () => {
        // Step 1: Just get the topics[cite: 1]
        const res = await fetch(`${API_BASE}/subjects?username=${user}`);
        const data = await res.json();
        setSubjects(data.subjects || []); 
        }}>Refresh Suggestions</button>

        <ul style={{ marginTop: 20 }}>
        {subjects.map((s, i) => (
            <li key={i} style={{ marginBottom: 15 }}>
            <strong>{s}</strong> <br/>
            {/* Step 2: Only generate when THIS button is clicked[cite: 1] */}
            <button onClick={async () => {
                alert(`Generating podcast for: ${s}`);
                await fetch(`${API_BASE}/generate-podcast?username=${user}&subject=${encodeURIComponent(s)}`, {
                    method: 'POST'
                });
                setView('library');
            }}>Generate This Episode</button>
            </li>
        ))}
        </ul>
        <button onClick={() => setView('interests')}>Back</button>
    </div>
    );

    // 4. LIBRARY PAGE
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
                            <audio controls src={`${API_BASE}/audio/${file}`} style={{ width: '100%' }} />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}