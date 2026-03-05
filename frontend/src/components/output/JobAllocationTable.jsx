import React from 'react';

const JobAllocationTable = ({ schedules }) => {
    // Flatten assignments
    const allAssignments = [];
    Object.keys(schedules).forEach(machineId => {
        schedules[machineId].forEach(job => {
            allAssignments.push({ ...job, machine_id: machineId });
        });
    });

    // Sort by start time
    allAssignments.sort((a, b) => {
        return a.start_time.localeCompare(b.start_time);
    });

    return (
        <div className="industrial-card mt-4">
            <h3>Job Allocation Details</h3>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead style={{ position: 'sticky', top: 0, background: 'var(--bg-card)', zIndex: 10 }}>
                        <tr style={{ textAlign: 'left', borderBottom: '2px solid var(--border-color)' }}>
                            <th className="p-2">Job ID</th>
                            <th className="p-2">Machine</th>
                            <th className="p-2">Product</th>
                            <th className="p-2">Start</th>
                            <th className="p-2">Finish</th>
                            <th className="p-2">Type</th>
                        </tr>
                    </thead>
                    <tbody>
                        {allAssignments.map((row, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)', background: row.is_setup ? 'rgba(255,255,255,0.03)' : 'transparent' }}>
                                <td className="p-2 font-bold">{row.is_setup ? '-' : row.job_id}</td>
                                <td className="p-2">{row.machine_id}</td>
                                <td className="p-2">
                                    {row.is_setup ? (
                                        <span style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>Setup</span>
                                    ) : (
                                        <span style={{
                                            color: row.product_type === 'P_A' ? '#3b82f6' :
                                                row.product_type === 'P_B' ? '#06b6d4' : '#8b5cf6'
                                        }}>
                                            {row.product_type}
                                        </span>
                                    )}
                                </td>
                                <td className="p-2">{row.start_time}</td>
                                <td className="p-2">{row.end_time}</td>
                                <td className="p-2">{row.is_setup ? 'Transition' : 'Production'}</td>
                            </tr>
                        ))}
                        {allAssignments.length === 0 && (
                            <tr>
                                <td colSpan="6" className="p-4 text-center text-muted">No jobs allocated yet.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default JobAllocationTable;
