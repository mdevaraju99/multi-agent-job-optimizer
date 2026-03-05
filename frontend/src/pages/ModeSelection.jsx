import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, Factory } from 'lucide-react';

const ModeSelection = () => {
    const navigate = useNavigate();

    const handleModeSelect = (mode) => {
        localStorage.setItem('optimizer_mode', mode);
        navigate('/dashboard');
    };

    return (
        <div className="flex-col" style={{ height: '100vh', justifyContent: 'center', alignItems: 'center', background: 'radial-gradient(circle at center, #1e293b 0%, #0f172a 100%)' }}>
            <h1 style={{ fontSize: '3rem', marginBottom: '2rem', background: 'linear-gradient(to right, #3b82f6, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Job Optimizer AI
            </h1>

            <div className="flex-row" style={{ gap: '2rem' }}>
                <div
                    className="industrial-card"
                    style={{ width: '300px', cursor: 'pointer', textAlign: 'center' }}
                    onClick={() => handleModeSelect('poc')}
                >
                    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem', color: '#3b82f6' }}>
                        <Settings size={64} />
                    </div>
                    <h2>POC Mode</h2>
                    <p className="text-muted">
                        Generate random synthetic data to demonstrate the agent's capabilities instantly.
                    </p>
                    <button className="btn-primary w-full mt-4">Start Demo</button>
                </div>

                <div
                    className="industrial-card"
                    style={{ width: '300px', cursor: 'pointer', textAlign: 'center' }}
                    onClick={() => handleModeSelect('industry')}
                >
                    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem', color: '#06b6d4' }}>
                        <Factory size={64} />
                    </div>
                    <h2>Industry Mode</h2>
                    <p className="text-muted">
                        Upload your own production CSV files for real-world schedule optimization.
                    </p>
                    <button className="btn-secondary w-full mt-4">Upload Data</button>
                </div>
            </div>
        </div>
    );
};

export default ModeSelection;
