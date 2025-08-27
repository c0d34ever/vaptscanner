// Minimal VAPT App for testing
console.log('Minimal app.js loaded');

// Global functions for HTML onclick handlers
function showNewScanModal() {
    console.log('showNewScanModal called');
    const modal = document.getElementById('newScanModal');
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    } else {
        console.error('Modal not found');
    }
}

function startScan() {
    console.log('startScan called');
    alert('Start scan functionality would go here');
}

function refreshData() {
    console.log('refreshData called');
    alert('Refresh data functionality would go here');
}

function showSection(sectionName) {
    console.log('showSection called:', sectionName);
    alert(`Show section: ${sectionName}`);
}

// Test if Bootstrap is available
window.addEventListener('load', () => {
    console.log('Page loaded in minimal app');
    if (typeof bootstrap !== 'undefined') {
        console.log('✅ Bootstrap is available');
    } else {
        console.log('❌ Bootstrap is NOT available');
    }
});
