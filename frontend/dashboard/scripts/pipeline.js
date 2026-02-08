/**
 * Pipeline Management
 * Handles job stage transitions and notes
 */

// Get pipeline state from localStorage
function getPipelineState() {
    const stored = localStorage.getItem('resumi_pipeline');
    return stored ? JSON.parse(stored) : {};
}

// Save pipeline state
function savePipelineState(state) {
    localStorage.setItem('resumi_pipeline', JSON.stringify(state));
}

// Get job notes
function getJobNotes(jobId) {
    const state = getPipelineState();
    return state[jobId]?.notes || [];
}

// Add note to job
function addJobNote(jobId, noteText) {
    const state = getPipelineState();

    if (!state[jobId]) {
        state[jobId] = { notes: [] };
    }

    const note = {
        text: noteText,
        timestamp: new Date().toISOString(),
        date: new Date().toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        })
    };

    state[jobId].notes.push(note);
    savePipelineState(state);

    return note;
}

// Get job stage history
function getJobStageHistory(jobId) {
    const state = getPipelineState();
    return state[jobId]?.stageHistory || [];
}

// Record stage change
function recordStageChange(jobId, fromStage, toStage) {
    const state = getPipelineState();

    if (!state[jobId]) {
        state[jobId] = { stageHistory: [] };
    }

    if (!state[jobId].stageHistory) {
        state[jobId].stageHistory = [];
    }

    state[jobId].stageHistory.push({
        from: fromStage,
        to: toStage,
        timestamp: new Date().toISOString(),
        date: new Date().toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        })
    });

    savePipelineState(state);
}

// Export functions for use in dashboard.js
window.PipelineManager = {
    getPipelineState,
    savePipelineState,
    getJobNotes,
    addJobNote,
    getJobStageHistory,
    recordStageChange
};
