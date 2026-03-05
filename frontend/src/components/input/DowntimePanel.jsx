import React, { useState } from 'react';
import { Clock, AlertTriangle, Upload } from 'lucide-react';
import { dataService } from '../../services/api';

const DowntimePanel = ({ mode, downtimes, setDowntimes, jobs }) => {
    const [loading, setLoading] = useState(false);
    const [dtCount, setDtCount] = useState(1);

    const getMachineCount = () => {
        // Get unique machines from jobs
        const machines = new Set();
        jobs.forEach(job => {
            job.machine_options.forEach(m => machines.add(m));
        });
        return machines.size || 4; // Default to 4 if no jobs loaded
    };

    const handleRandomDowntime = async () => {
        setLoading(true);
        try {
            const machineCount = getMachineCount();
            const res = await dataService.generateDowntime(dtCount, machineCount);
            setDowntimes(prev => [...prev, ...res.data]);
        } catch (err) {
            alert("Error generating downtime: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await dataService.uploadDowntime(formData);
            setDowntimes(res.data);
        } catch (err) {
            alert("Upload failed: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="industrial-card mt-4">
            <div className="flex-row justify-between mb-4">
                <h3>Machine Availability</h3>
                <span className="text-xs text-muted">{downtimes.length} Events</span>
            </div>

            {mode === 'poc' && (
                <div className="flex-col mb-4">
                    <div className="flex-row justify-between mb-2">
                        <label className="text-sm text-muted">Count:</label>
                        <input
                            type="number"
                            className="input-field"
                            style={{ width: '80px', padding: '0.25rem' }}
                            value={dtCount}
                            onChange={(e) => setDtCount(parseInt(e.target.value) || 1)}
                        />
                    </div>
                    <button
                        className="btn-secondary flex-row justify-center"
                        onClick={handleRandomDowntime}
                        disabled={loading}
                        style={{ borderColor: 'var(--status-warning)', color: 'var(--status-warning)' }}
                    >
                        <AlertTriangle size={16} style={{ marginRight: '0.5rem' }} /> Generate Random Downtime
                    </button>
                </div>
            )}

            {mode === 'industry' && (
                <div>
                    <div style={{ position: 'relative', marginBottom: '1rem' }}>
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileUpload}
                            style={{ opacity: 0, position: 'absolute', width: '100%', height: '100%', cursor: 'pointer' }}
                        />
                        <button className="btn-secondary w-full flex-row justify-center">
                            <Upload size={16} /> Upload Downtime CSV
                        </button>
                    </div>
                    <div className="p-3" style={{ background: 'rgba(234, 179, 8, 0.1)', borderRadius: '4px', border: '1px solid rgba(234, 179, 8, 0.3)' }}>
                        <p className="text-xs font-bold mb-2">CSV Format Required:</p>
                        <p className="text-xs text-muted mb-1">• machine_id, start_time (HH:MM), end_time (HH:MM)</p>
                        <p className="text-xs text-muted mb-1">• Optional: reason (e.g., Equipment Cleaning)</p>
                        <p className="text-xs text-muted">• Example: M2,10:30,11:00,Quality Calibration</p>
                    </div>
                </div>
            )}

            <div className="flex-col">
                {downtimes.map((dt, idx) => (
                    <div key={idx} style={{
                        borderLeft: '3px solid var(--status-warning)',
                        padding: '0.5rem',
                        background: 'rgba(234, 179, 8, 0.1)',
                        fontSize: '0.8rem'
                    }}>
                        <div className="flex-row justify-between">
                            <span className="font-bold">{dt.machine_id}</span>
                            <span>{dt.start_time} - {dt.end_time}</span>
                        </div>
                        <div className="text-muted text-xs">{dt.reason}</div>
                    </div>
                ))}
                {downtimes.length === 0 && <p className="text-xs text-muted text-center">No downtime scheduled.</p>}
            </div>
        </div>
    );
};

export default DowntimePanel;
