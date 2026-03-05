import React, { useState } from 'react';
import { Play, Activity, Layers, GitMerge, BarChart2, Zap } from 'lucide-react';
import { simulationService } from '../../services/api';

const OptimizationPanel = ({ onRun, onOpenDowntimeModal, loading, disabled, activeAgent, viewMode }) => {
    const agents = [
        { id: 'baseline', name: 'Baseline (FCFS)', icon: Play, desc: 'Simple FIFO scheduler' },
        { id: 'batching', name: 'Batching (AI)', icon: Layers, desc: 'Minimizes setup times' },
        { id: 'bottleneck', name: 'Bottleneck (AI)', icon: Activity, desc: 'Balances load' },
        { id: 'orchestrated', name: 'Orchestrated', icon: GitMerge, desc: 'Multi-agent collaboration' },
    ];

    return (
        <div className="flex-row justify-between mb-4">
            <div className="flex-row">
                {agents.map(agent => (
                    <button
                        key={agent.id}
                        onClick={() => onRun(agent.id)}
                        disabled={loading || disabled}
                        className={`btn-secondary ${activeAgent === agent.id && viewMode !== 'compare' ? 'btn-primary' : ''}`}
                        style={{
                            opacity: disabled ? 0.5 : 1,
                            background: activeAgent === agent.id && viewMode !== 'compare' ? 'var(--accent-blue)' : undefined,
                            border: activeAgent === agent.id && viewMode !== 'compare' ? 'none' : undefined
                        }}
                        title={agent.desc}
                    >
                        <div className="flex-row" style={{ gap: '0.5rem' }}>
                            <agent.icon size={16} />
                            {agent.name}
                        </div>
                    </button>
                ))}
                <button
                    onClick={() => onRun('compare')}
                    disabled={loading || disabled}
                    className={`btn-secondary ${viewMode === 'compare' ? 'btn-primary' : ''}`}
                    style={{
                        background: viewMode === 'compare' ? 'var(--accent-blue)' : undefined,
                        border: viewMode === 'compare' ? 'none' : undefined
                    }}
                >
                    <div className="flex-row" style={{ gap: '0.5rem' }}>
                        <BarChart2 size={16} /> Compare All
                    </div>
                </button>
            </div>

            {/* Simulation Trigger */}
            <button
                className="btn-secondary"
                style={{ borderColor: 'var(--status-error)', color: 'var(--status-error)' }}
                onClick={onOpenDowntimeModal}
                disabled={disabled}
            >
                <div className="flex-row" style={{ gap: '0.5rem' }}>
                    <Zap size={16} /> Simulate Failure
                </div>
            </button>
        </div>
    );
};

export default OptimizationPanel;
