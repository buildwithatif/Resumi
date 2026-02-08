/**
 * Dashboard JavaScript
 * Handles job display, filtering, and details panel
 */

// Sample job data (in production, this would come from API)
const sampleJobs = [
    {
        id: 'job-1',
        title: 'Strategy Manager',
        company: 'McKinsey & Company',
        location: 'Mumbai, India',
        type: 'Consulting',
        source: 'Greenhouse',
        sourceType: 'verified',
        postedDate: '3 days ago',
        matchScore: 85,
        matchReason: 'Strong strategy skills, Mumbai location',
        description: 'Lead business strategy initiatives for Fortune 500 clients...',
        stage: 'discovered'
    },
    {
        id: 'job-2',
        title: 'Operations Lead',
        company: 'Razorpay',
        location: 'Bangalore, India',
        type: 'Operations',
        source: 'Lever',
        sourceType: 'verified',
        postedDate: '1 week ago',
        matchScore: 78,
        matchReason: 'Operations experience, India location',
        description: 'Manage supply chain and logistics operations...',
        stage: 'discovered'
    },
    {
        id: 'job-3',
        title: 'Marketing Manager',
        company: 'Swiggy',
        location: 'Bangalore, India',
        type: 'Marketing',
        source: 'Greenhouse',
        sourceType: 'verified',
        postedDate: '5 days ago',
        matchScore: 72,
        matchReason: 'Marketing skills, growth experience',
        description: 'Drive growth marketing initiatives...',
        stage: 'discovered'
    }
];

// Current view state
let currentView = 'discover';
let currentJobs = [];
let selectedJob = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadJobs();
    setupNavigation();
    setupDetailsPanel();
    updateCounts();
});

// Load jobs from localStorage or use sample data
function loadJobs() {
    const stored = localStorage.getItem('resumi_jobs');
    currentJobs = stored ? JSON.parse(stored) : sampleJobs;
    saveJobs();
    renderJobs();
}

// Save jobs to localStorage
function saveJobs() {
    localStorage.setItem('resumi_jobs', JSON.stringify(currentJobs));
}

// Render job cards
function renderJobs() {
    const jobList = document.getElementById('job-list');
    const filteredJobs = currentJobs.filter(job => {
        if (currentView === 'discover') return job.stage === 'discovered';
        return job.stage === currentView;
    });

    if (filteredJobs.length === 0) {
        jobList.innerHTML = `
            <div style="text-align: center; padding: 48px; color: var(--text-secondary);">
                <p>No jobs in this stage yet.</p>
            </div>
        `;
        return;
    }

    jobList.innerHTML = filteredJobs.map(job => createJobCard(job)).join('');

    // Add event listeners
    document.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const jobId = e.target.dataset.jobId;
            showJobDetails(jobId);
        });
    });

    document.querySelectorAll('.stage-selector').forEach(select => {
        select.addEventListener('change', (e) => {
            const jobId = e.target.dataset.jobId;
            const newStage = e.target.value;
            updateJobStage(jobId, newStage);
        });
    });
}

// Create job card HTML
function createJobCard(job) {
    return `
        <div class="job-card" data-job-id="${job.id}">
            <div class="job-header">
                <h3 class="job-title">${job.title}</h3>
                <span class="job-source ${job.sourceType}">
                    ${job.sourceType === 'verified' ? '✓' : '🔍'} ${job.source}
                </span>
            </div>
            
            <div class="job-company">${job.company}</div>
            
            <div class="job-meta">
                <span class="meta-item">📍 ${job.location}</span>
                <span class="meta-item">💼 ${job.type}</span>
                <span class="meta-item">⏰ ${job.postedDate}</span>
            </div>
            
            <div class="job-match">
                <div class="match-score">
                    <span class="score-value">${job.matchScore}%</span>
                    <span class="score-label">Match</span>
                </div>
                <div class="match-reason">${job.matchReason}</div>
            </div>
            
            <div class="job-actions">
                <select class="stage-selector" data-job-id="${job.id}">
                    <option value="discovered" ${job.stage === 'discovered' ? 'selected' : ''}>Discovered</option>
                    <option value="saved" ${job.stage === 'saved' ? 'selected' : ''}>Save</option>
                    <option value="applied" ${job.stage === 'applied' ? 'selected' : ''}>Applied</option>
                    <option value="interviewing" ${job.stage === 'interviewing' ? 'selected' : ''}>Interviewing</option>
                    <option value="offer" ${job.stage === 'offer' ? 'selected' : ''}>Offer</option>
                    <option value="rejected" ${job.stage === 'rejected' ? 'selected' : ''}>Not Interested</option>
                </select>
                <button class="btn btn-primary view-details-btn" data-job-id="${job.id}">
                    View Details
                </button>
            </div>
        </div>
    `;
}

// Setup navigation
function setupNavigation() {
    document.querySelectorAll('.nav-item[data-view]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = e.currentTarget.dataset.view;
            switchView(view);
        });
    });
}

// Switch view
function switchView(view) {
    currentView = view;

    // Update active nav item
    document.querySelectorAll('.nav-item[data-view]').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-view="${view}"]`).classList.add('active');

    // Update header
    const titles = {
        discover: 'Discover Jobs',
        saved: 'Saved Jobs',
        applied: 'Applied Jobs',
        interviewing: 'Interviews',
        offer: 'Offers',
        rejected: 'Not Interested'
    };

    document.getElementById('view-title').textContent = titles[view];

    // Render jobs for this view
    renderJobs();
}

// Update job stage
function updateJobStage(jobId, newStage) {
    const job = currentJobs.find(j => j.id === jobId);
    if (job) {
        job.stage = newStage;
        saveJobs();
        updateCounts();
        renderJobs();
    }
}

// Update counts in sidebar
function updateCounts() {
    const counts = {
        discovered: 0,
        saved: 0,
        applied: 0,
        interviewing: 0,
        offer: 0,
        rejected: 0
    };

    currentJobs.forEach(job => {
        if (counts.hasOwnProperty(job.stage)) {
            counts[job.stage]++;
        }
    });

    document.getElementById('discover-count').textContent = counts.discovered;
    document.getElementById('saved-count').textContent = counts.saved;
    document.getElementById('applied-count').textContent = counts.applied;
    document.getElementById('interviewing-count').textContent = counts.interviewing;
    document.getElementById('offer-count').textContent = counts.offer;
    document.getElementById('rejected-count').textContent = counts.rejected;
}

// Setup details panel
function setupDetailsPanel() {
    document.getElementById('close-panel').addEventListener('click', closeDetailsPanel);
}

// Show job details
function showJobDetails(jobId) {
    const job = currentJobs.find(j => j.id === jobId);
    if (!job) return;

    selectedJob = job;

    document.getElementById('detail-title').textContent = job.title;
    document.getElementById('detail-company').textContent = job.company;

    document.getElementById('panel-content').innerHTML = `
        <section class="details-section">
            <h3>Job Details</h3>
            <div class="detail-row">
                <span class="label">Location</span>
                <span class="value">${job.location}</span>
            </div>
            <div class="detail-row">
                <span class="label">Type</span>
                <span class="value">${job.type}</span>
            </div>
            <div class="detail-row">
                <span class="label">Posted</span>
                <span class="value">${job.postedDate}</span>
            </div>
            <div class="detail-row">
                <span class="label">Source</span>
                <span class="value">${job.source}</span>
            </div>
        </section>
        
        <section class="details-section">
            <h3>Why This Match?</h3>
            <ul class="match-reasons">
                <li>✓ Match Score: ${job.matchScore}%</li>
                <li>✓ ${job.matchReason}</li>
            </ul>
        </section>
        
        <section class="details-section">
            <h3>Description</h3>
            <div class="job-description">
                <p>${job.description}</p>
            </div>
        </section>
    `;

    document.getElementById('job-details-panel').classList.add('open');
}

// Close details panel
function closeDetailsPanel() {
    document.getElementById('job-details-panel').classList.remove('open');
    selectedJob = null;
}
