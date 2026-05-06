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
    const handleMetrics = () => {
        setView('metrics');
    };
    const saveInterests = async (updatedList) => {
        try {
            const response = await fetch(`${API_BASE}/update-interests`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json' 
                },
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
    const MetricsButton = () => (
        <button 
            onClick={handleMetrics}
            style={{
                position: 'absolute',
                top: '60px',
                right: '20px',
                padding: '8px 15px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer'
            }}
        >
            View Metrics
        </button>
    );
    const [selectedSubject, setSelectedSubject] = useState('');
    const [turns, setTurns] = useState(10);
    const [debugLog, setDebugLog] = useState('');
    const mockMetrics = {
        totalGenerations: 1248,
        avgTurnsPerEpisode: 12.5,
        storageUsed: "4.2 GB",
        popularTopics: ["AI Ethics", "Space Exploration", "European Economy"],
        dailyActiveUsers: [45, 52, 48, 70, 85, 92, 88]
    };
    const cardStyle = { background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' };
    const metricStyle = { fontSize: '32px', fontWeight: 'bold', color: '#007bff', margin: '10px 0' };
    const fetchSubjects = React.useCallback(async () => {
        if (!user) return;
        console.log("Fetching subjects automatically...");
        try {
            const res = await fetch(`${API_BASE}/subjects?username=${user}`);
            const data = await res.json();
            setSubjects(data.subjects || []); 
        } catch (err) {
            console.error("Failed to fetch subjects:", err);
        }
    }, [user]);
    useEffect(() => {
        if (view === 'generate' && subjects.length === 0) {
            fetchSubjects();
        }
    }, [view, subjects.length, fetchSubjects]);


    if (view === 'login') return (
        <div style={{ padding: 40, fontFamily: 'sans-serif' }}>
            <h1>Login</h1>
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

    if (view === 'interests') return (
        <div style={{ padding: 40, fontFamily: 'sans-serif', position: 'relative' }}>
            <LogoutButton />
            <MetricsButton/>
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


    if (view === 'generate') return (
        <div style={{ padding: 40, fontFamily: 'sans-serif', position: 'relative' }}>
            <LogoutButton />
            <MetricsButton/>
            <h1>Pick a Topic</h1>
            {subjects.length === 0 ? (
                <p>Looking for topics based on your interests...</p>
            ) : (
                <ul style={{ marginTop: 20 }}>
                    {subjects.map((s, i) => (
                        <li key={i} style={{ marginBottom: 15 }}>
                            <strong>{s}</strong> <br/>
                            <button onClick={() => {
                                setSelectedSubject(s);
                                setView('configure');
                            }}>Configure This Episode</button>
                        </li>
                    ))}
                </ul>
            )}
            
            <button onClick={() => setView('interests')}>Back</button>
            <button onClick={fetchSubjects} style={{ marginLeft: 10 }}>Refresh Manually</button>
        </div>
    );

    if (view === 'library') return (
        <div style={{ padding: 40, fontFamily: 'sans-serif', position: 'relative' }}>
            <LogoutButton />
            <MetricsButton/>
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

    if (view === 'configure') return (
        <div style={{ padding: 40, fontFamily: 'sans-serif' }}>
            <LogoutButton />
            <MetricsButton/>
            <h1>Configure: {selectedSubject}</h1>
            
            {!generating ? (
                <div>
                    <p>How long should the podcast be approximately? (Miinutes)</p>
                    <input 
                        type="number" 
                        value={turns} 
                        onChange={(e) => setTurns(e.target.value)}
                        style={{ padding: 10, width: '60px', marginRight: 10 }}
                    />
                    <button 
                        style={{ padding: '10px 20px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '5px' }}
                        onClick={async () => {
                            setGenerating(true);
                            setDebugLog("Starting research and script generation...");
                            
                            try {
                                const res = await fetch(`${API_BASE}/generate-podcast?username=${user}&subject=${encodeURIComponent(selectedSubject)}&turns=${turns}`, {
                                    method: 'POST'
                                });
                                if (res.ok) {
                                    setView('library');
                                }
                            } catch (err) {
                                setDebugLog("Error: " + err.message);
                            } finally {
                                setGenerating(false);
                            }
                        }}
                    >
                        🚀 Start Generation
                    </button>
                    <button onClick={() => setView('generate')} style={{ marginLeft: 10 }}>Cancel</button>
                </div>
            ) : (
                <div style={{ marginTop: 20 }}>
                    <div className="spinner" style={{ marginBottom: 20 }}>⏳ Generating your podcast... please wait.</div>
                    
                    {/* Debug Info Section */}
                    <div style={{ 
                        background: '#1e1e1e', 
                        color: '#00ff00', 
                        padding: 15, 
                        borderRadius: 5, 
                        fontFamily: 'monospace',
                        fontSize: '12px',
                        maxHeight: '200px',
                        overflowY: 'auto'
                    }}>
                        <strong>Debug Stream:</strong>
                        <p>{debugLog}</p>
                        <p>Processing subject: {selectedSubject}</p>
                        <p>Requested turns: {turns}</p>
                        <p>Contacting AI nodes...</p>
                    </div>
                </div>
            )}
        </div>
    );

    if (view === 'metrics') return (
        <div style={{ padding: 40, fontFamily: 'sans-serif', backgroundColor: '#f4f7f6', minHeight: '100vh' }}>
            <LogoutButton />
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1>Product Success Dashboard (Mocked)</h1>
                <button 
                    onClick={() => setView('interests')} 
                    style={{
                        position: 'absolute',
                        top: '60px',
                        right: '20px',
                        padding: '8px 15px',
                        backgroundColor: '#6c757d',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                    }}
                >
                    Exit Admin
                </button>
            </div>

            {/* Metric Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginTop: 20 }}>
                <div style={cardStyle}>
                    <h3>Total Episodes</h3>
                    <p style={metricStyle}>{mockMetrics.totalGenerations}</p>
                </div>
                <div style={cardStyle}>
                    <h3>Avg. Episode Length</h3>
                    <p style={metricStyle}>{mockMetrics.avgTurnsPerEpisode} Turns (~{mockMetrics.avgTurnsPerEpisode} minutes)</p>
                </div>
                <div style={cardStyle}>
                    <h3>Storage Used</h3>
                    <p style={metricStyle}>{mockMetrics.storageUsed}</p>
                </div>
            </div>

            {/* Detailed Insights */}
            <div style={{ marginTop: 30, display: 'flex', gap: '20px' }}>
                <div style={{ ...cardStyle, flex: 2 }}>
                    <h3>Popular Research Topics</h3>
                    <ul>
                        {mockMetrics.popularTopics.map((topic, i) => (
                            <li key={i} style={{ padding: '8px 0', borderBottom: '1px solid #eee' }}>{topic}</li>
                        ))}
                    </ul>
                </div>
                <div style={{ ...cardStyle, flex: 1 }}>
                    <h3>System Status</h3>
                    <p>🟢 Researcher API: Online</p>
                    <p>🟢 Dialog API: Online</p>
                    <p>🟢 Audio API: Online</p>
                    <p>🟢 Local user database: Connected</p>
                </div>
            </div>
        </div>
    );
}