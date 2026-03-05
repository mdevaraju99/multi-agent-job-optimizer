import React, { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';

const DowntimeInputModal = ({ isOpen, onClose, onSubmit, availableMachines }) => {
    const [machineId, setMachineId] = useState('M1');
    const [startTime, setStartTime] = useState('10:00');
    const [endTime, setEndTime] = useState('11:00');
    const [reason, setReason] = useState('Equipment Cleaning');

    const handleSubmit = () => {
        if (!machineId || !startTime || !endTime) {
            alert('Please fill all fields');
            return;
        }

        // Validate time range
        const [startH, startM] = startTime.split(':').map(Number);
        const [endH, endM] = endTime.split(':').map(Number);
        const startMins = startH * 60 + startM;
        const endMins = endH * 60 + endM;

        if (endMins <= startMins) {
            alert('End time must be after start time');
            return;
        }

        onSubmit({
            machine_id: machineId,
            start_time: startTime,
            end_time: endTime,
            reason: reason
        });

        onClose();
    };

    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
        }}>
            <div className="industrial-card" style={{ width: '500px', maxWidth: '90%' }}>
                <div className="flex-row justify-between mb-4">
                    <div className="flex-row" style={{ gap: '0.5rem' }}>
                        <AlertTriangle size={20} style={{ color: 'var(--status-error)' }} />
                        <h3>Simulate Machine Failure</h3>
                    </div>
                    <button onClick={onClose} className="btn-secondary" style={{ padding: '0.25rem' }}>
                        <X size={18} />
                    </button>
                </div>

                <div className="flex-col" style={{ gap: '1rem' }}>
                    <div className="flex-col" style={{ gap: '0.5rem' }}>
                        <label className="text-sm text-muted">Machine:</label>
                        <select 
                            className="input-field"
                            value={machineId}
                            onChange={(e) => setMachineId(e.target.value)}
                            style={{ padding: '0.5rem', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '4px' }}
                        >
                            {availableMachines.map(m => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex-col" style={{ gap: '0.5rem' }}>
                        <label className="text-sm text-muted">Start Time (HH:MM):</label>
                        <input
                            type="time"
                            className="input-field"
                            value={startTime}
                            onChange={(e) => setStartTime(e.target.value)}
                            style={{ padding: '0.5rem' }}
                        />
                    </div>

                    <div className="flex-col" style={{ gap: '0.5rem' }}>
                        <label className="text-sm text-muted">End Time (HH:MM):</label>
                        <input
                            type="time"
                            className="input-field"
                            value={endTime}
                            onChange={(e) => setEndTime(e.target.value)}
                            style={{ padding: '0.5rem' }}
                        />
                    </div>

                    <div className="flex-col" style={{ gap: '0.5rem' }}>
                        <label className="text-sm text-muted">Reason:</label>
                        <select
                            className="input-field"
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
                            style={{ padding: '0.5rem', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '4px' }}
                        >
                            <option value="Equipment Cleaning">Equipment Cleaning</option>
                            <option value="Maintenance">Maintenance</option>
                            <option value="Quality Calibration">Quality Calibration</option>
                            <option value="Sterilization">Sterilization</option>
                            <option value="Unexpected Breakdown">Unexpected Breakdown</option>
                        </select>
                    </div>

                    <div className="flex-row justify-end" style={{ gap: '0.5rem', marginTop: '1rem' }}>
                        <button className="btn-secondary" onClick={onClose}>
                            Cancel
                        </button>
                        <button 
                            className="btn-primary" 
                            onClick={handleSubmit}
                            style={{ background: 'var(--status-error)', border: 'none' }}
                        >
                            Simulate Downtime
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DowntimeInputModal;
