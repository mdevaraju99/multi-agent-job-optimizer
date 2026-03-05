import React from 'react';
import { X } from 'lucide-react';

const JobInputModal = ({ isOpen, onClose, jobs }) => {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.7)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div className="industrial-card" style={{ width: '90vw', maxWidth: '1200px', maxHeight: '90vh', overflowY: 'auto', position: 'relative' }}>
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', color: 'var(--accent-blue)', fontSize: 20, cursor: 'pointer' }}
        >
          <X size={24} />
        </button>
        <h2 style={{ marginBottom: '1rem' }}>Full Job Intake Table</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ textAlign: 'left', background: 'var(--bg-card-hover)' }}>
              <th>Job ID</th>
              <th>Product</th>
              <th>Duration</th>
              <th>Deadline</th>
              <th>Priority</th>
              <th>Compatible Machines</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map(j => (
              <tr key={j.job_id} style={{ borderTop: '1px solid #334155' }}>
                <td className="p-4">{j.job_id}</td>
                <td>{j.product_type}</td>
                <td>{j.processing_time}min</td>
                <td>{j.due_time || '-'}</td>
                <td style={{ color: j.priority === 'Rush' ? 'var(--status-error)' : 'inherit' }}>{j.priority}</td>
                <td className="text-xs">{j.machine_options.join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default JobInputModal;
