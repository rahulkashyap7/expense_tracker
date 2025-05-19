// Custom JavaScript for Expense Tracker

// Enable Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // File input validation
    const receiptInput = document.getElementById('receipt');
    if (receiptInput) {
        receiptInput.addEventListener('change', function() {
            const fileSize = this.files[0].size / 1024 / 1024; // in MB
            if (fileSize > 5) {
                alert('File size exceeds 5 MB. Please choose a smaller file.');
                this.value = '';
            }
        });
    }
});