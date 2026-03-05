import React from 'react';

const GanttChart = ({ schedules, downtimes }) => {
    // schedule: { m_id: [ScheduledJob] }
    // shift: 08:00 to 16:00 (480 mins) or stretch if overtime.
    // We assume 08:00 start for absolute positioning.

    const START_HOUR = 8;
    const END_HOUR = 18; // Allow some overtime view
    const TOTAL_MINUTES = (END_HOUR - START_HOUR) * 60;

    // Pharma product color mapping
    const PRODUCT_COLORS = {
        'Paracetamol_500mg': '#3b82f6',    // Blue
        'Ibuprofen_400mg': '#10b981',       // Green
        'Amoxicillin_250mg': '#f59e0b',     // Amber
        'Aspirin_75mg': '#ec4899',          // Pink
        'Metformin_500mg': '#8b5cf6',       // Purple
    };

    const getProductColor = (productType) => {
        return PRODUCT_COLORS[productType] || '#06b6d4'; // Cyan as fallback
    };

    const timeToPercent = (timeStr) => {
        const [h, m] = timeStr.split(':').map(Number);
        const mins = (h - START_HOUR) * 60 + m;
        return (mins / TOTAL_MINUTES) * 100;
    };

    const durationToPercent = (start, end) => {
        return timeToPercent(end) - timeToPercent(start);
    };

    const machines = Object.keys(schedules).sort();

    return (
        <div className="industrial-card mt-4 overflow-hidden">
            <h3>Machine Schedule (Gantt)</h3>

            <div style={{ position: 'relative', marginTop: '1rem' }}>
                {/* Timeline Header */}
                <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '0.5rem', paddingLeft: '50px' }}>
                    {Array.from({ length: END_HOUR - START_HOUR + 1 }).map((_, i) => (
                        <div key={i} style={{ flex: 1, borderLeft: '1px dashed var(--border-color)', fontSize: '0.75rem', color: '#94a3b8', paddingLeft: '2px' }}>
                            {START_HOUR + i}:00
                        </div>
                    ))}
                </div>

                {/* Machine Rows */}
                {machines.map(mid => (
                    <div key={mid} style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem', height: '40px' }}>
                        <div style={{ width: '50px', fontWeight: 'bold' }}>{mid}</div>
                        <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', height: '100%', position: 'relative', borderRadius: '4px' }}>
                            {/* Jobs */}
                            {schedules[mid].map((job, jIdx) => (
                                <div
                                    key={job.job_id}
                                    style={{
                                        position: 'absolute',
                                        left: `${timeToPercent(job.start_time)}%`,
                                        width: `${durationToPercent(job.start_time, job.end_time)}%`,
                                        height: '80%',
                                        top: '10%',
                                        backgroundColor: job.is_setup ? 'var(--text-secondary)' : getProductColor(job.product_type),
                                        borderRadius: '3px',
                                        fontSize: '0.7rem',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        color: 'white',
                                        cursor: 'help',
                                        overflow: 'hidden',
                                        whiteSpace: 'nowrap'
                                    }}
                                    title={`${job.job_id} (${job.product_type})\n${job.start_time} - ${job.end_time}`}
                                >
                                    {job.is_setup ? 'Setup' : job.job_id}
                                </div>
                            ))}

                            {/* Downtimes */}
                            {downtimes.filter(d => d.machine_id === mid).map((dt, dIdx) => (
                                <div
                                    key={`dt-${dIdx}`}
                                    style={{
                                        position: 'absolute',
                                        left: `${timeToPercent(dt.start_time)}%`,
                                        width: `${durationToPercent(dt.start_time, dt.end_time)}%`,
                                        height: '100%',
                                        top: 0,
                                        background: 'repeating-linear-gradient(45deg, #334155, #334155 5px, #1e293b 5px, #1e293b 10px)',
                                        opacity: 0.7,
                                        zIndex: 0
                                    }}
                                    title={`Downtime: ${dt.reason}`}
                                />
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {/* Legend */}
            <div className="flex-row mt-4 text-xs justify-center">
                <div className="flex-row" style={{ gap: '0.5rem' }}><span style={{ width: 10, height: 10, background: '#3b82f6', display: 'inline-block' }}></span> Paracetamol</div>
                <div className="flex-row" style={{ gap: '0.5rem' }}><span style={{ width: 10, height: 10, background: '#10b981', display: 'inline-block' }}></span> Ibuprofen</div>
                <div className="flex-row" style={{ gap: '0.5rem' }}><span style={{ width: 10, height: 10, background: '#f59e0b', display: 'inline-block' }}></span> Amoxicillin</div>
                <div className="flex-row" style={{ gap: '0.5rem' }}><span style={{ width: 10, height: 10, background: '#ec4899', display: 'inline-block' }}></span> Aspirin</div>
                <div className="flex-row" style={{ gap: '0.5rem' }}><span style={{ width: 10, height: 10, background: '#8b5cf6', display: 'inline-block' }}></span> Metformin</div>
                <div className="flex-row" style={{ gap: '0.5rem' }}><span style={{ width: 10, height: 10, background: 'repeating-linear-gradient(45deg, #334155, #334155 5px, #1e293b 5px, #1e293b 10px)', display: 'inline-block' }}></span> Downtime</div>
            </div>
        </div>
    );
};

export default GanttChart;
