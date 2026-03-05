import React from 'react';

const ExplanationPanel = ({ explanation }) => (
    <div className="industrial-card mt-4">
        <h3>AI Explanation</h3>
        <p style={{ whiteSpace: 'pre-line', lineHeight: '1.6', color: '#cbd5e1' }}>
            {explanation}
        </p>
    </div>
);

export default ExplanationPanel;
