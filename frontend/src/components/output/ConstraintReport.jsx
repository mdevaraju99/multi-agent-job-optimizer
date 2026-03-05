import React from 'react';
import { CheckCircle, AlertOctagon } from 'lucide-react';

const ConstraintReport = ({ violations }) => (
    <div className="industrial-card mt-4">
        <h3>Constraint Validation</h3>
        {violations.length === 0 ? (
            <div className="flex-row" style={{ color: 'var(--status-success)' }}>
                <CheckCircle size={20} />
                <span>All constraints satisfied (Shift limits, Downtime, Compatibility).</span>
            </div>
        ) : (
            <ul style={{ paddingLeft: '0', listStyle: 'none' }}>
                {violations.map((v, i) => (
                    <li key={i} className="flex-row" style={{ color: 'var(--status-error)', marginBottom: '0.5rem', alignItems: 'flex-start' }}>
                        <AlertOctagon size={16} style={{ marginTop: '3px', flexShrink: 0 }} />
                        <span>{v}</span>
                    </li>
                ))}
            </ul>
        )}
    </div>
);

export default ConstraintReport;
