// VAPT Scanner Frontend Application
class VAPTApp {
    constructor() {
        this.apiKey = 'vapt-key-u3JkN9qX4sW8yZ2tL6aP0vB3mH7cD1rF5xG9kT2nV4pS8qL0wE3';
        this.baseUrl = window.location.origin;
        this.charts = {};
        this.currentSection = 'dashboard';
        
        this.init();
    }

    init() {
        this.loadTemplates();
        this.loadDashboard();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Auto-refresh every 30 seconds
        setInterval(() => this.refreshData(), 30000);
        
        // Form submission
        document.getElementById('new-scan-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.startScan();
        });
    }

    async makeApiCall(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            this.showNotification(`API Error: ${error.message}`, 'error');
            throw error;
        }
    }

    showNotification(message, type = 'info') {
        const alertClass = type === 'error' ? 'alert-danger' : 
                          type === 'success' ? 'alert-success' : 'alert-info';
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }

    async loadDashboard() {
        try {
            const [stats, scans] = await Promise.all([
                this.makeApiCall('/api/stats/'),
                this.makeApiCall('/api/scans/')
            ]);

            this.updateStats(stats);
            this.updateRecentScans(scans);
            this.createCharts(stats);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        }
    }

    updateStats(stats) {
        document.getElementById('total-scans').textContent = stats.total_scans || 0;
        document.getElementById('completed-scans').textContent = stats.completed_scans || 0;
        document.getElementById('in-progress-scans').textContent = stats.in_progress_scans || 0;
        document.getElementById('critical-findings').textContent = stats.critical_findings || 0;
    }

    updateRecentScans(scans) {
        const tbody = document.getElementById('recent-scans-body');
        if (!tbody) return;

        tbody.innerHTML = scans.slice(0, 10).map(scan => `
            <tr>
                <td>${scan.id}</td>
                <td>
                    <a href="${scan.target_url}" target="_blank" class="text-truncate d-inline-block" style="max-width: 200px;">
                        ${scan.target_url}
                    </a>
                </td>
                <td><span class="badge bg-secondary">${scan.engine}</span></td>
                <td>${this.getStatusBadge(scan.status)}</td>
                <td>
                    <span class="badge bg-info">${scan.findings_count || 0}</span>
                    ${scan.critical_findings_count > 0 ? 
                        `<span class="badge bg-danger ms-1">${scan.critical_findings_count}</span>` : ''}
                </td>
                <td>${this.formatDate(scan.start_time)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="app.viewScan(${scan.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="app.downloadReport(${scan.id})">
                        <i class="fas fa-download"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    getStatusBadge(status) {
        const badges = {
            'PENDING': 'bg-secondary',
            'IN_PROGRESS': 'bg-warning',
            'COMPLETED': 'bg-success',
            'FAILED': 'bg-danger',
            'CANCELLED': 'bg-dark'
        };
        return `<span class="badge ${badges[status] || 'bg-secondary'}">${status}</span>`;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    createCharts(stats) {
        // Scan Activity Chart
        const activityCtx = document.getElementById('scanActivityChart');
        if (activityCtx && !this.charts.activity) {
            this.charts.activity = new Chart(activityCtx, {
                type: 'line',
                data: {
                    labels: this.getLast30Days(),
                    datasets: [{
                        label: 'Scans Started',
                        data: this.generateRandomData(30, 5, 15),
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        // Engine Distribution Chart
        const engineCtx = document.getElementById('engineChart');
        if (engineCtx && !this.charts.engine) {
            const engineData = stats.engine_breakdown || [
                { engine: 'zap', count: 25 },
                { engine: 'nmap', count: 15 },
                { engine: 'sqlmap', count: 10 },
                { engine: 'wapiti', count: 8 }
            ];

            this.charts.engine = new Chart(engineCtx, {
                type: 'doughnut',
                data: {
                    labels: engineData.map(d => d.engine.toUpperCase()),
                    datasets: [{
                        data: engineData.map(d => d.count),
                        backgroundColor: [
                            '#667eea',
                            '#764ba2',
                            '#f093fb',
                            '#f5576c'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }
    }

    getLast30Days() {
        const dates = [];
        for (let i = 29; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        return dates;
    }

    generateRandomData(length, min, max) {
        return Array.from({ length }, () => Math.floor(Math.random() * (max - min + 1)) + min);
    }

    async loadTemplates() {
        try {
            const templates = await this.makeApiCall('/api/templates/');
            const select = document.getElementById('scan-template');
            if (select) {
                select.innerHTML = '<option value="">No Template</option>' +
                    templates.map(t => `<option value="${t.id}">${t.name} (${t.engine})</option>`).join('');
            }
        } catch (error) {
            console.error('Failed to load templates:', error);
        }
    }

    async startScan() {
        const form = document.getElementById('new-scan-form');
        const formData = new FormData(form);
        
        const scanData = {
            target_url: document.getElementById('target-url').value,
            engine: document.getElementById('scan-engine').value,
            template_id: document.getElementById('scan-template').value || null,
            options: this.parseOptions(document.getElementById('scan-options').value)
        };

        try {
            const result = await this.makeApiCall('/api/scans/create/', {
                method: 'POST',
                body: JSON.stringify(scanData)
            });

            this.showNotification(`Scan started successfully! ID: ${result.id}`, 'success');
            
            // Close modal and refresh
            const modal = bootstrap.Modal.getInstance(document.getElementById('newScanModal'));
            modal.hide();
            form.reset();
            
            // Refresh dashboard
            setTimeout(() => this.refreshData(), 1000);
            
        } catch (error) {
            this.showNotification('Failed to start scan', 'error');
        }
    }

    parseOptions(optionsString) {
        if (!optionsString.trim()) return {};
        try {
            return JSON.parse(optionsString);
        } catch (e) {
            this.showNotification('Invalid JSON in options field', 'error');
            return {};
        }
    }

    async viewScan(scanId) {
        try {
            const scan = await this.makeApiCall(`/api/scans/${scanId}/`);
            this.showScanDetails(scan);
        } catch (error) {
            this.showNotification('Failed to load scan details', 'error');
        }
    }

    async downloadReport(scanId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/scans/${scanId}/export/?format=json`, {
                headers: { 'X-API-Key': this.apiKey }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `scan_${scanId}_report.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            this.showNotification('Failed to download report', 'error');
        }
    }

    showScanDetails(scan) {
        // Create and show a modal with scan details
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Scan Details - ${scan.target_url}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Basic Information</h6>
                                <table class="table table-sm">
                                    <tr><td>ID:</td><td>${scan.id}</td></tr>
                                    <tr><td>Status:</td><td>${this.getStatusBadge(scan.status)}</td></tr>
                                    <tr><td>Engine:</td><td>${scan.engine}</td></tr>
                                    <tr><td>Started:</td><td>${this.formatDate(scan.start_time)}</td></tr>
                                    <tr><td>Completed:</td><td>${this.formatDate(scan.end_time)}</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6>Findings Summary</h6>
                                <div class="alert alert-info">
                                    Total Findings: <strong>${scan.findings_count || 0}</strong><br>
                                    Critical Findings: <strong>${scan.critical_findings_count || 0}</strong>
                                </div>
                            </div>
                        </div>
                        ${scan.report_json ? `
                            <h6>Detailed Report</h6>
                            <pre class="bg-light p-3 rounded"><code>${JSON.stringify(scan.report_json, null, 2)}</code></pre>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('[id$="-section"]').forEach(el => el.style.display = 'none');
        
        // Show selected section
        const section = document.getElementById(`${sectionName}-section`);
        if (section) section.style.display = 'block';
        
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
        event.target.classList.add('active');
        
        // Update page title
        document.getElementById('page-title').textContent = sectionName.charAt(0).toUpperCase() + sectionName.slice(1);
        
        this.currentSection = sectionName;
        
        // Load section-specific data
        if (sectionName === 'scans') this.loadScansSection();
        else if (sectionName === 'templates') this.loadTemplatesSection();
        else if (sectionName === 'scheduled') this.loadScheduledSection();
        else if (sectionName === 'bulk') this.loadBulkSection();
        else if (sectionName === 'reports') this.loadReportsSection();
    }

    async loadScansSection() {
        const section = document.getElementById('scans-section');
        if (!section) return;
        
        section.innerHTML = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="m-0 font-weight-bold text-primary">All Scans</h6>
                    <div class="input-group" style="width: 300px;">
                        <input type="text" class="form-control" placeholder="Search scans..." id="scan-search">
                        <button class="btn btn-outline-secondary" type="button" onclick="app.searchScans()">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped" id="all-scans-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Target</th>
                                    <th>Engine</th>
                                    <th>Status</th>
                                    <th>Findings</th>
                                    <th>Started</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="all-scans-body">
                                <tr><td colspan="7" class="text-center">Loading...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        // Load all scans
        try {
            const scans = await this.makeApiCall('/api/scans/');
            this.updateAllScansTable(scans);
        } catch (error) {
            console.error('Failed to load scans:', error);
        }
    }

    updateAllScansTable(scans) {
        const tbody = document.getElementById('all-scans-body');
        if (!tbody) return;
        
        tbody.innerHTML = scans.map(scan => `
            <tr>
                <td>${scan.id}</td>
                <td>
                    <a href="${scan.target_url}" target="_blank" class="text-truncate d-inline-block" style="max-width: 200px;">
                        ${scan.target_url}
                    </a>
                </td>
                <td><span class="badge bg-secondary">${scan.engine}</span></td>
                <td>${this.getStatusBadge(scan.status)}</td>
                <td>
                    <span class="badge bg-info">${scan.findings_count || 0}</span>
                    ${scan.critical_findings_count > 0 ? 
                        `<span class="badge bg-danger ms-1">${scan.critical_findings_count}</span>` : ''}
                </td>
                <td>${this.formatDate(scan.start_time)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="app.viewScan(${scan.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="app.downloadReport(${scan.id})">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="app.viewLogs(${scan.id})">
                            <i class="fas fa-list"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    async searchScans() {
        const query = document.getElementById('scan-search')?.value;
        if (!query) return;
        
        try {
            const results = await this.makeApiCall(`/api/search/?q=${encodeURIComponent(query)}`);
            this.updateAllScansTable(results);
        } catch (error) {
            this.showNotification('Search failed', 'error');
        }
    }

    async viewLogs(scanId) {
        try {
            const logs = await this.makeApiCall(`/api/scans/${scanId}/logs/`);
            this.showLogsModal(scanId, logs);
        } catch (error) {
            this.showNotification('Failed to load logs', 'error');
        }
    }

    showLogsModal(scanId, logs) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Scan Logs - Scan #${scanId}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Timestamp</th>
                                        <th>Level</th>
                                        <th>Message</th>
                                        <th>Context</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${logs.map(log => `
                                        <tr>
                                            <td>${this.formatDate(log.timestamp)}</td>
                                            <td><span class="badge bg-${this.getLogLevelBadge(log.level)}">${log.level}</span></td>
                                            <td>${log.message}</td>
                                            <td>${log.context ? JSON.stringify(log.context) : ''}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    getLogLevelBadge(level) {
        const badges = {
            'INFO': 'info',
            'WARNING': 'warning',
            'ERROR': 'danger',
            'DEBUG': 'secondary'
        };
        return badges[level] || 'secondary';
    }

    refreshData() {
        if (this.currentSection === 'dashboard') {
            this.loadDashboard();
        } else if (this.currentSection === 'scans') {
            this.loadScansSection();
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new VAPTApp();
});

// Global functions for HTML onclick handlers
function showSection(sectionName) {
    window.app?.showSection(sectionName);
}

function showNewScanModal() {
    const modal = new bootstrap.Modal(document.getElementById('newScanModal'));
    modal.show();
}

function startScan() {
    window.app?.startScan();
}

function refreshData() {
    window.app?.refreshData();
}
