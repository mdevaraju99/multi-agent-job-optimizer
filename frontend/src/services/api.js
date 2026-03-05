import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const dataService = {
    generateRandomData: (count = 20, rushProb = 0.2, downtimeCount = 0, machineCount = 4) =>
        api.post(`/data/generate-random?job_count=${count}&rush_prob=${rushProb}&downtime_count=${downtimeCount}&machine_count=${machineCount}`),
    generateDowntime: (count = 1, machineCount = 4) => api.post(`/data/generate-downtime?count=${count}&machine_count=${machineCount}`),
    uploadJobs: (formData) => api.post('/data/upload-jobs', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    uploadDowntime: (formData) => api.post('/data/upload-downtime', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
};

export const optimizeService = {
    runBaseline: (payload) => api.post('/optimize/baseline', payload),
    runBatching: (payload) => api.post('/optimize/batching', payload),
    runBottleneck: (payload) => api.post('/optimize/bottleneck', payload),
    runOrchestrated: (payload) => api.post('/optimize/orchestrated', payload),
    runComparison: (payload) => api.post('/optimize/compare-all', payload),
};

export const simulationService = {
    simulateFailure: (payload, machineId) => api.post(`/simulate/machine-failure?machine_id=${machineId}`, payload),
};

export default api;
