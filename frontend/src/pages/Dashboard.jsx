import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Play, AlertTriangle } from 'lucide-react';
import { dataService, optimizeService, simulationService } from '../services/api';

// Components (will be implemented)
import JobInputPanel from '../components/input/JobInputPanel';
import DowntimePanel from '../components/input/DowntimePanel';
import DowntimeInputModal from '../components/input/DowntimeInputModal';
import OptimizationPanel from '../components/control/OptimizationPanel';
import GanttChart from '../components/output/GanttChart';
import KPISummary from '../components/output/KPISummary';
import ExplanationPanel from '../components/output/ExplanationPanel';
import ComparisonTable from '../components/output/ComparisonTable';
import ConstraintReport from '../components/output/ConstraintReport';
import JobInputModal from '../components/input/JobInputModal';

import JobAllocationTable from '../components/output/JobAllocationTable';

const Dashboard = () => {
    const navigate = useNavigate();
    const [mode, setMode] = useState('poc');
    const [jobs, setJobs] = useState([]);
    const [downtimes, setDowntimes] = useState([]);
    const [downtimeModalOpen, setDowntimeModalOpen] = useState(false);
    const [scheduleResult, setScheduleResult] = useState(null); // Single agent result
    const [comparisonResult, setComparisonResult] = useState(null); // Comparison result
    const [viewMode, setViewMode] = useState('single'); // 'single' or 'compare'
    const [loading, setLoading] = useState(false);
    const [activeAgent, setActiveAgent] = useState('baseline');
    const [sidebarExpanded, setSidebarExpanded] = useState(false);
    const [jobModalOpen, setJobModalOpen] = useState(false);

    useEffect(() => {
        const storedMode = localStorage.getItem('optimizer_mode');
        if (storedMode) setMode(storedMode);

        const handler = () => setJobModalOpen(true);
        window.addEventListener('openJobModal', handler);
        return () => window.removeEventListener('openJobModal', handler);
    }, []);

    const handleAddDowntime = (downtimeData) => {
        // Add the new downtime to existing downtimes
        setDowntimes([...downtimes, downtimeData]);
        alert(`Machine failure added on ${downtimeData.machine_id} (${downtimeData.start_time} - ${downtimeData.end_time}). Re-run optimization to see impact.`);
    };

    const getAvailableMachines = () => {
        // Get unique machines from jobs
        const machines = new Set();
        jobs.forEach(job => {
            job.machine_options.forEach(m => machines.add(m));
        });
        return Array.from(machines).sort();
    };

    const handleOptimization = async (agentType) => {
        setLoading(true);
        setActiveAgent(agentType);
        setViewMode('single');

        try {
            const payload = {
                jobs,
                downtimes,
                shift: { start_time: "08:00", end_time: "16:00" }
            };

            let res;
            switch (agentType) {
                case 'baseline': res = await optimizeService.runBaseline(payload); break;
                case 'batching': res = await optimizeService.runBatching(payload); break;
                case 'bottleneck': res = await optimizeService.runBottleneck(payload); break;
                case 'orchestrated': res = await optimizeService.runOrchestrated(payload); break;
                case 'compare':
                    res = await optimizeService.runComparison(payload);
                    setComparisonResult(res.data);
                    setViewMode('compare');
                    setLoading(false);
                    return;
            }
            setScheduleResult(res.data);
        } catch (err) {
            console.error(err);
            alert("Optimization Failed: " + err.message);
        } finally {
            if (agentType !== 'compare') setLoading(false);
        }
    };

    const verifyData = () => {
        return jobs.length > 0;
    };

    return (
        <div className="flex-col" style={{ padding: '2rem', height: '100vh', overflow: 'hidden' }}>
            {/* Header */}
            <div className="flex-row justify-between" style={{ borderBottom: '1px solid #334155', paddingBottom: '1rem' }}>
                <div className="flex-row">
                    <button className="btn-secondary" onClick={() => navigate('/')}>
                        <ArrowLeft size={16} /> Back
                    </button>
                    <h2>Production Optimizer <span className="text-muted text-sm">({mode.toUpperCase()} Mode)</span></h2>
                </div>
                <div className="flex-row">
                    {/* Global Actions */}
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: sidebarExpanded ? '1fr' : '350px 1fr', gap: '2rem', height: 'calc(100vh - 100px)' }}>
                {/* Left Column: Inputs */}
                <div className="flex-col" style={{ overflowY: 'auto', paddingRight: '0.5rem', width: sidebarExpanded ? '100%' : '350px', transition: 'width 0.3s' }}>
                    <div className="flex-row justify-between mb-2">
                        <h3>Input Panels</h3>
                        <button
                            className="btn-secondary"
                            style={{ fontSize: '0.8rem', padding: '0.5rem 1rem' }}
                            onClick={() => setSidebarExpanded(e => !e)}
                        >
                            {sidebarExpanded ? 'Collapse' : 'Expand'}
                        </button>
                    </div>
                    <JobInputPanel
                        mode={mode}
                        jobs={jobs}
                        setJobs={setJobs}
                    />
                    <DowntimePanel
                        mode={mode}
                        downtimes={downtimes}
                        setDowntimes={setDowntimes}
                        jobs={jobs}
                    />
                </div>

                {/* Right Column: Control & Output */}
                <div className="flex-col" style={{ overflowY: 'auto' }}>
                    {/* Control Panel */}
                    <OptimizationPanel
                        onRun={handleOptimization}
                        onOpenDowntimeModal={() => setDowntimeModalOpen(true)}
                        loading={loading}
                        disabled={!verifyData()}
                        activeAgent={activeAgent}
                        viewMode={viewMode}
                    />

                    {/* Results Area */}
                    {loading ? (
                        <div className="industrial-card text-center p-4">
                            <h3>AI Agents Working...</h3>
                            <p className="text-muted">Analyzing constraints, batching sequences, and optimizing loads.</p>
                        </div>
                    ) : (
                        <>
                            {viewMode === 'compare' && comparisonResult ? (
                                <ComparisonTable data={comparisonResult} onSelectAgent={(res) => {
                                    setScheduleResult(res);
                                    setViewMode('single'); // Switch to view details
                                }} />
                            ) : scheduleResult ? (
                                <div className="flex-col">
                                    <div className="grid-cols-4">
                                        <KPISummary kpis={scheduleResult.kpis} />
                                    </div>
                                    <GanttChart schedules={scheduleResult.schedules} downtimes={downtimes} />
                                    <JobAllocationTable schedules={scheduleResult.schedules} />
                                    <div className="grid-cols-2">
                                        <ExplanationPanel explanation={scheduleResult.explanation} />
                                        <ConstraintReport violations={scheduleResult.violations} />
                                    </div>
                                </div>
                            ) : (
                                <div className="industrial-card text-center p-4" style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <p className="text-muted">Load data and start optimization to see results.</p>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>

            {/* Downtime Input Modal */}
            <DowntimeInputModal
                isOpen={downtimeModalOpen}
                onClose={() => setDowntimeModalOpen(false)}
                onSubmit={handleAddDowntime}
                availableMachines={getAvailableMachines()}
            />

            {/* Job Intake Modal */}
            <JobInputModal
                isOpen={jobModalOpen}
                onClose={() => setJobModalOpen(false)}
                jobs={jobs}
            />
        </div>
    );
};

export default Dashboard;
