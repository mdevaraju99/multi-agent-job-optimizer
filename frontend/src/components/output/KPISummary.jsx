import React from 'react';

const KPISummary = ({ kpis }) => (
    <>
        <div className="industrial-card text-center">
            <div className="text-muted text-xs uppercase">Optimization Score</div>
            <div style={{ fontSize: '2rem', color: 'var(--accent-cyan)', fontWeight: 'bold' }}>
                {kpis.score}
            </div>
        </div>
        <div className="industrial-card text-center">
            <div className="text-muted text-xs uppercase">Makespan</div>
            <div style={{ fontSize: '1.5rem' }}>{kpis.makespan} <span className="text-sm">min</span></div>
        </div>
        <div className="industrial-card text-center">
            <div className="text-muted text-xs uppercase">Tardiness</div>
            <div style={{ fontSize: '1.5rem', color: kpis.total_tardiness > 0 ? 'var(--status-warning)' : 'var(--status-success)' }}>
                {kpis.total_tardiness} <span className="text-sm">min</span>
            </div>
        </div>
        <div className="industrial-card text-center">
            <div className="text-muted text-xs uppercase">Setup Time</div>
            <div style={{ fontSize: '1.5rem' }}>{kpis.total_setup_time} <span className="text-sm">min</span></div>
        </div>
    </>
);

export default KPISummary;
