/**
 * Web Browser Query Agent - Frontend JavaScript
 * Handles user interactions and API communication
 */

class QueryAgent {
    constructor() {
        this.isProcessing = false;
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.bindEventListeners();
        this.applyTheme();
        this.focusQueryInput();
    }

    bindEventListeners() {
        // Query input and search
        const queryInput = document.getElementById('queryInput');
        const searchBtn = document.getElementById('searchBtn');

        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isProcessing) {
                this.processQuery();
            }
        });

        searchBtn.addEventListener('click', () => {
            if (!this.isProcessing) {
                this.processQuery();
            }
        });

        // Example queries
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                queryInput.value = query;
                this.processQuery();
            });
        });

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        themeToggle.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Status button
        const statusBtn = document.getElementById('statusBtn');
        statusBtn.addEventListener('click', () => {
            this.showSystemStatus();
        });

        // Modal controls
        const closeModal = document.getElementById('closeModal');
        const statusModal = document.getElementById('statusModal');

        closeModal.addEventListener('click', () => {
            this.hideModal();
        });

        statusModal.addEventListener('click', (e) => {
            if (e.target === statusModal) {
                this.hideModal();
            }
        });

        // Retry button
        const retryBtn = document.getElementById('retryBtn');
        retryBtn.addEventListener('click', () => {
            this.processQuery();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'k':
                        e.preventDefault();
                        queryInput.focus();
                        break;
                    case '/':
                        e.preventDefault();
                        queryInput.focus();
                        break;
                }
            }
            if (e.key === 'Escape') {
                this.hideModal();
            }
        });
    }

    async processQuery() {
        const queryInput = document.getElementById('queryInput');
        const query = queryInput.value.trim();

        if (!query) {
            this.showToast('Please enter a query', 'warning');
            queryInput.focus();
            return;
        }

        if (this.isProcessing) {
            return;
        }

        this.isProcessing = true;
        this.showLoading();
        this.hideResults();
        this.hideError();

        try {
            // Simulate processing steps
            this.updateLoadingStep('step1', true);
            await this.sleep(500);

            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });

            this.updateLoadingStep('step2', true);
            await this.sleep(500);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            this.updateLoadingStep('step3', true);
            await this.sleep(500);

            this.updateLoadingStep('step4', true);
            await this.sleep(500);

            this.hideLoading();
            this.displayResult(result);

        } catch (error) {
            console.error('Error processing query:', error);
            this.hideLoading();
            this.showError('Failed to process query', error.message);
            this.showToast('Query processing failed', 'error');
        } finally {
            this.isProcessing = false;
        }
    }

    displayResult(result) {
        if (result.type === 'invalid_query') {
            this.showError('Invalid Query', result.response, result.reason);
            return;
        }

        if (result.type === 'error') {
            this.showError('Processing Error', result.response);
            return;
        }

        if (result.type === 'no_results') {
            this.showError('No Results', result.response);
            return;
        }

        // Display successful result
        const resultTitle = document.getElementById('resultTitle');
        const resultContent = document.getElementById('resultContent');
        const processingTime = document.getElementById('processingTime');
        const cacheStatus = document.getElementById('cacheStatus');
        const sourcesList = document.getElementById('sourcesList');

        resultTitle.textContent = 'Search Results';
        resultContent.innerHTML = this.formatAnswer(result.answer || result.response);

        processingTime.innerHTML = `<i class="fas fa-clock"></i> ${result.processing_time?.toFixed(2) || 0}s`;

        if (result.cached) {
            cacheStatus.innerHTML = `<i class="fas fa-database"></i> Cached result`;
            cacheStatus.style.color = 'var(--success-color)';
        } else {
            cacheStatus.innerHTML = `<i class="fas fa-globe"></i> Fresh result`;
            cacheStatus.style.color = 'var(--primary-color)';
        }

        // Display sources
        if (result.sources && result.sources.length > 0) {
            sourcesList.innerHTML = '';
            result.sources.forEach((source, index) => {
                const sourceItem = this.createSourceItem(source, index + 1);
                sourcesList.appendChild(sourceItem);
            });
            document.getElementById('sourcesSection').classList.remove('hidden');
        } else {
            document.getElementById('sourcesSection').classList.add('hidden');
        }

        this.showResults();
        this.showToast('Query processed successfully', 'success');
    }

    formatAnswer(answer) {
        // Simple formatting for better readability
        return answer
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    createSourceItem(source, number) {
        const sourceItem = document.createElement('div');
        sourceItem.className = 'source-item';

        sourceItem.innerHTML = `
            <div class="source-number">${number}</div>
            <div class="source-content">
                <div class="source-title">${this.escapeHtml(source.title)}</div>
                <a href="${source.url}" target="_blank" rel="noopener noreferrer" class="source-url">
                    ${this.truncateUrl(source.url)}
                    <i class="fas fa-external-link-alt" style="margin-left: 4px; font-size: 0.8em;"></i>
                </a>
            </div>
        `;

        return sourceItem;
    }

    async showSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();

            const statusContent = document.getElementById('statusContent');
            statusContent.innerHTML = this.formatSystemStatus(status);

            this.showModal();
        } catch (error) {
            console.error('Error fetching system status:', error);
            this.showToast('Failed to fetch system status', 'error');
        }
    }

    formatSystemStatus(status) {
        let html = `
            <div class="status-overview">
                <h4>System Status: <span style="color: var(--${status.status === 'online' ? 'success' : 'error'}-color)">${status.status}</span></h4>
            </div>

            <div class="status-section">
                <h5><i class="fas fa-cogs"></i> Components</h5>
                <div class="components-grid">
        `;

        if (status.components) {
            Object.entries(status.components).forEach(([component, componentStatus]) => {
                const icon = componentStatus === 'online' ? 'fas fa-check-circle' : 'fas fa-times-circle';
                const color = componentStatus === 'online' ? 'var(--success-color)' : 'var(--error-color)';

                html += `
                    <div class="component-item">
                        <i class="${icon}" style="color: ${color}"></i>
                        <span>${component.replace(/_/g, ' ')}</span>
                        <span style="color: ${color}">${componentStatus}</span>
                    </div>
                `;
            });
        }

        html += `
                </div>
            </div>

            <div class="status-section">
                <h5><i class="fas fa-sliders-h"></i> Configuration</h5>
                <div class="config-grid">
        `;

        if (status.config) {
            Object.entries(status.config).forEach(([key, value]) => {
                html += `
                    <div class="config-item">
                        <span>${key.replace(/_/g, ' ')}</span>
                        <span>${value}</span>
                    </div>
                `;
            });
        }

        html += `
                </div>
            </div>
        `;

        if (status.cache_stats && !status.cache_stats.error) {
            html += `
                <div class="status-section">
                    <h5><i class="fas fa-database"></i> Cache Statistics</h5>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span>Cached Queries</span>
                            <span>${status.cache_stats.total_cached_queries || 0}</span>
                        </div>
                    </div>
                </div>
            `;
        }

        return html;
    }

    showLoading() {
        document.getElementById('loadingIndicator').classList.remove('hidden');
        this.resetLoadingSteps();
    }

    hideLoading() {
        document.getElementById('loadingIndicator').classList.add('hidden');
    }

    resetLoadingSteps() {
        document.querySelectorAll('.step').forEach(step => {
            step.classList.remove('active');
        });
    }

    updateLoadingStep(stepId, active) {
        const step = document.getElementById(stepId);
        if (step) {
            if (active) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        }
    }

    showResults() {
        document.getElementById('resultsSection').classList.remove('hidden');
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    hideResults() {
        document.getElementById('resultsSection').classList.add('hidden');
    }

    showError(title, message, details = null) {
        const errorTitle = document.getElementById('errorTitle');
        const errorMessage = document.getElementById('errorMessage');

        errorTitle.textContent = title;
        errorMessage.innerHTML = `
            <p>${this.escapeHtml(message)}</p>
            ${details ? `<p class="text-muted" style="margin-top: 1rem; font-size: 0.9em;">${this.escapeHtml(details)}</p>` : ''}
        `;

        document.getElementById('errorSection').classList.remove('hidden');
        document.getElementById('errorSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    hideError() {
        document.getElementById('errorSection').classList.add('hidden');
    }

    showModal() {
        document.getElementById('statusModal').classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    hideModal() {
        document.getElementById('statusModal').classList.add('hidden');
        document.body.style.overflow = '';
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme();
        localStorage.setItem('theme', this.currentTheme);
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle.querySelector('i');

        if (this.currentTheme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }

    showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    focusQueryInput() {
        const queryInput = document.getElementById('queryInput');
        queryInput.focus();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    truncateUrl(url, maxLength = 60) {
        if (url.length <= maxLength) return url;
        return url.substring(0, maxLength) + '...';
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Additional CSS for status modal components
const additionalCSS = `
.status-overview {
    margin-bottom: 2rem;
    text-align: center;
}

.status-section {
    margin-bottom: 2rem;
}

.status-section h5 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    color: var(--text-primary);
    font-size: 1.1rem;
}

.components-grid,
.config-grid,
.stats-grid {
    display: grid;
    gap: 0.75rem;
}

.component-item,
.config-item,
.stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
}

.component-item i {
    margin-right: 0.5rem;
}
`;

// Inject additional CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalCSS;
document.head.appendChild(styleSheet);

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new QueryAgent();
});
