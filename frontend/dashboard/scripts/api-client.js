/**
 * Resumi API Client
 * Handles all API communication with the backend
 */

class ResumiAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.sessionId = localStorage.getItem('resumi_session_id');
    }

    /**
     * Upload resume and get profile
     */
    async uploadResume(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseURL}/api/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Resume upload failed');
        }

        const data = await response.json();
        this.sessionId = data.session_id;
        localStorage.setItem('resumi_session_id', data.session_id);
        localStorage.setItem('resumi_profile', JSON.stringify(data.profile));

        return data;
    }

    /**
     * Discover jobs using unified API
     */
    async discoverJobs(request) {
        const response = await fetch(`${this.baseURL}/api/discover-jobs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error('Job discovery failed');
        }

        return await response.json();
    }

    /**
     * Get external search URLs
     */
    async getExternalSearches(request) {
        const response = await fetch(`${this.baseURL}/api/external-searches`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error('External search generation failed');
        }

        return await response.json();
    }

    /**
     * Get stored profile
     */
    getStoredProfile() {
        const profile = localStorage.getItem('resumi_profile');
        return profile ? JSON.parse(profile) : null;
    }

    /**
     * Clear session
     */
    clearSession() {
        localStorage.removeItem('resumi_session_id');
        localStorage.removeItem('resumi_profile');
        this.sessionId = null;
    }
}

// Export for use in other scripts
window.ResumiAPI = ResumiAPI;
