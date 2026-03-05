import React from 'react';
import { Check, X } from 'lucide-react';

const ComparisonTable = ({ data, onSelectAgent }) => {
    // data matches ComparisonResponse schema: { baseline, batching, bottleneck, orchestrated, summary }

    const agents = ['baseline', 'batching', 'bottleneck', 'orchestrated'];

    const getAgentRes = (key) => data[key];

    return (
        <div className="industrial-card">
            <h3>Agent Performance Comparison</h3>
            <p className="text-muted text-sm mb-4">{data.summary}</p>

            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr style={{ background: 'var(--bg-card-hover)', textAlign: 'left' }}>
                        <th className="p-4">Metric</th>
                        {agents.map(a => <th key={a} className="p-4" style={{ textTransform: 'capitalize' }}>{a}</th>)}
                    </tr>
                </thead>
                <tbody>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td className="p-4 font-bold">Score (0-100)</td>
                        {agents.map(a => {
                            const res = getAgentRes(a);
                            return <td key={a} className="p-4" style={{ color: 'var(--accent-blue)', fontWeight: 'bold' }}>{res.kpis.score}</td>
                        })}
                    </tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td className="p-4">Makespan (min)</td>
                        {agents.map(a => <td key={a} className="p-4">{getAgentRes(a).kpis.makespan}</td>)}
                    </tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td className="p-4">Setup Time (min)</td>
                        {agents.map(a => <td key={a} className="p-4">{getAgentRes(a).kpis.total_setup_time}</td>)}
                    </tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td className="p-4">Tardiness (min)</td>
                        {agents.map(a => <td key={a} className="p-4">{getAgentRes(a).kpis.total_tardiness}</td>)}
                    </tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td className="p-4">Product Switches</td>
                        {agents.map(a => <td key={a} className="p-4">{getAgentRes(a).kpis.product_switches || 0}</td>)}
                    </tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td className="p-4">Load Balance Variance</td>
                        {agents.map(a => <td key={a} className="p-4">{getAgentRes(a).kpis.load_balance_variance?.toFixed(1) || 'N/A'}</td>)}
                    </tr>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td className="p-4">Violations</td>
                        {agents.map(a => {
                            const v = getAgentRes(a).violations.length;
                            return <td key={a} className="p-4" style={{ color: v > 0 ? 'var(--status-error)' : 'var(--status-success)' }}>{v}</td>
                        })}
                    </tr>
                    <tr>
                        <td className="p-4"></td>
                        {agents.map(a => (
                            <td key={a} className="p-4">
                                <button className="btn-secondary text-xs" onClick={() => onSelectAgent(getAgentRes(a))}>
                                    View Details
                                </button>
                            </td>
                        ))}
                    </tr>
                </tbody>
            </table>
        </div>
    );
};

export default ComparisonTable;
