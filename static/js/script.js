// Main script for CusAkuntanID application

// Document ready function
document.addEventListener("DOMContentLoaded", function() {
    // Toggle sidebar on button click
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarCollapse && sidebar) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(function(element) {
                // Create a Bootstrap alert instance and close it
                const alert = new bootstrap.Alert(element);
                alert.close();
            });
        }, 5000);
    }
    
    // Format currency input fields
    const currencyInputs = document.querySelectorAll('input[data-type="currency"]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            // Remove non-numeric characters
            let value = this.value.replace(/[^0-9]/g, '');
            
            // Format with thousand separator
            if (value.length > 0) {
                value = parseInt(value, 10).toLocaleString('id-ID');
            }
            
            this.value = value;
        });
        
        // On form submit, convert back to number
        const form = input.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                const numericValue = input.value.replace(/\./g, '');
                input.value = numericValue;
            });
        }
    });
    
    // Initialize date pickers
    const datePickers = document.querySelectorAll('input[type="date"]');
    datePickers.forEach(function(picker) {
        // If there's no value and data-default="today" attribute is present, set to today
        if (!picker.value && picker.getAttribute('data-default') === 'today') {
            const today = new Date();
            const dd = String(today.getDate()).padStart(2, '0');
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const yyyy = today.getFullYear();
            picker.value = yyyy + '-' + mm + '-' + dd;
        }
    });
    
    // Dynamic table search
    const tableSearchInputs = document.querySelectorAll('input[data-search-table]');
    tableSearchInputs.forEach(function(input) {
        const tableId = input.getAttribute('data-search-table');
        const table = document.getElementById(tableId);
        
        if (table) {
            input.addEventListener('keyup', function() {
                const searchText = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(function(row) {
                    const cells = row.querySelectorAll('td');
                    let found = false;
                    
                    cells.forEach(function(cell, index) {
                        // Skip action column by checking for buttons
                        if (!cell.querySelector('button, a')) {
                            if (cell.textContent.toLowerCase().indexOf(searchText) > -1) {
                                found = true;
                            }
                        }
                    });
                    
                    row.style.display = found ? '' : 'none';
                });
            });
        }
    });
    
    // Toggle password visibility
    const togglePasswordBtns = document.querySelectorAll('.toggle-password');
    togglePasswordBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const passwordField = document.querySelector(this.getAttribute('data-target'));
            if (passwordField) {
                const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordField.setAttribute('type', type);
                
                // Change icon
                const icon = this.querySelector('i');
                if (icon) {
                    if (type === 'text') {
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                    } else {
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                    }
                }
            }
        });
    });
});

// Function to update invoice status via API
function updateTagihanStatus(tagihanId, status) {
    return fetch(`/api/set-status/${tagihanId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    });
}

// Function to format number as currency
function formatCurrency(number) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(number);
}

// Function to parse currency input to number
function parseCurrency(currencyString) {
    return parseInt(currencyString.replace(/[^\d]/g, ''), 10) || 0;
}
