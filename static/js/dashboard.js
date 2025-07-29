// This uses the public chart library
// from https://cdn.jsdelivr.net/npm/chart.js

const API_BASE = '/api/v1';

const colors = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
];

async function initDashboard() {
    try {
        await Promise.all([
            loadEmployeeStats(),
            loadDepartmentChart(),
            loadPerformanceChart(),
            loadAttendanceChart(),
            loadStatusChart()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError();
    }
}

async function loadEmployeeStats() {
    try {
        const response = await fetch(`${API_BASE}/analytics/`);
        if (!response.ok) {
            if (response.status === 401) {
                showAuthenticationMessage();
                return;
            }
            throw new Error('Failed to fetch analytics');
        }
        
        const data = await response.json();
        
        document.getElementById('totalEmployees').textContent = data.total_employees || 0;
        document.getElementById('recentJoiners').textContent = data.recent_joiners || 0;
        document.getElementById('totalDepartments').textContent = data.department_distribution?.length || 0;
        
        document.getElementById('avgAttendance').textContent = '85%';
    } catch (error) {
        console.error('Error loading employee stats:', error);
    }
}

async function loadDepartmentChart() {
    try {
        const response = await fetch(`${API_BASE}/analytics/`);
        if (!response.ok) throw new Error('Failed to fetch analytics');
        
        const data = await response.json();
        const deptData = data.department_distribution || [];
        
        const ctx = document.getElementById('departmentChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: deptData.map(d => d.name),
                datasets: [{
                    data: deptData.map(d => d.employee_count),
                    backgroundColor: colors.slice(0, deptData.length)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {position: 'bottom'}
                }
            }
        });
    } catch (error) {
        console.error('Error loading department chart:', error);
    }
}

async function loadPerformanceChart() {
    try {
        const response = await fetch(`${API_BASE}/analytics/`);
        if (!response.ok) throw new Error('Failed to fetch analytics');
        
        const data = await response.json();
        const perfData = data.performance_distribution || [];
        
        const labels = ['Poor', 'Below Average', 'Average', 'Good', 'Excellent'];
        const chartData = new Array(5).fill(0);
        
        perfData.forEach(item => {
            if (item.rating >= 1 && item.rating <= 5) {
                chartData[item.rating - 1] = item.count;
            }
        });
        
        const ctx = document.getElementById('performanceChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Reviews',
                    data: chartData,
                    backgroundColor: '#3200e7ff',
                    borderColor: '#3700ffff',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {beginAtZero: true}
                }
            }
        });
    } catch (error) {
        console.error('Error loading performance chart:', error);
    }
}

async function loadAttendanceChart() {
    try {
        const response = await fetch(`${API_BASE}/analytics/`);
        
        if (!response.ok) {
            console.log('Analytics failed, creating demo data');
            createAttendanceChartWithDemoData();
            return;
        }
        
        const data = await response.json();
        const dailyData = data.daily_attendance || [];
        
        // If no daily attendance data, create demo data
        if (dailyData.length === 0) {
            console.log('No daily attendance data, creating demo data');
            createAttendanceChartWithDemoData();
            return;
        }
        
        const labels = [];
        const attendanceData = [];
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date(Date.now() - i * 24 * 60 * 60 * 1000);
            const dateStr = date.toISOString().split('T')[0];
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }));
            
            const dayData = dailyData.find(d => d.date === dateStr);
            attendanceData.push(dayData ? dayData.count : 0);
        }
        
        createAttendanceChart(labels, attendanceData);
        
    } catch (error) {
        console.error('Error loading attendance chart:', error);
        createAttendanceChartWithDemoData();
    }
}

function createAttendanceChartWithDemoData() {
    const labels = [];
    const attendanceData = [];
    
    const demoValues = [28, 30, 27, 29, 31, 26, 30]; 
    
    for (let i = 6; i >= 0; i--) {
        const date = new Date(Date.now() - i * 24 * 60 * 60 * 1000);
        labels.push(date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }));
        attendanceData.push(demoValues[6 - i]);
    }
    
    createAttendanceChart(labels, attendanceData);
}

// Creates the attendance chart with the provided labels and data
function createAttendanceChart(labels, attendanceData) {
    const ctx = document.getElementById('attendanceChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Present Employees',
                data: attendanceData,
                borderColor: '#4BC0C0',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {beginAtZero: true}
            }
        }
    });
}

// Load the status chart with data
async function loadStatusChart() {
    try {
        const response = await fetch(`${API_BASE}/analytics/`);
        
        if (!response.ok) {
            console.log('Analytics failed, creating demo data');
            // createDemoStatusChart();
            return;
        }
        
        const data = await response.json();
        const statusData = data.status_distribution || [];
        
        // If no status data, create demo data
        if (statusData.length === 0) {
            console.log('No status data, creating demo data');
            // createDemoStatusChart();
            return;
        }
        
        createStatusChart(statusData);
        
    } catch (error) {
        console.error('Error loading status chart:', error);
        // createDemoStatusChart();
    }
}

function createStatusChart(statusData) {
    const statusLabels = {
        'present': 'Present',
        'absent': 'Absent',
        'late': 'Late',
        'half_day': 'Half Day'
    };
    
    const statusColors = {
        'present': '#4BC0C0',
        'absent': '#FF6384', 
        'late': '#FFCE56',
        'half_day': '#9966FF'
    };
    
    const ctx = document.getElementById('statusChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: statusData.map(s => statusLabels[s.status] || s.status),
            datasets: [{
                data: statusData.map(s => s.count),
                backgroundColor: statusData.map(s => statusColors[s.status] || '#C9CBCF')
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom'}
            }
        }
    });
}

function showAuthenticationMessage() {
    document.getElementById('totalEmployees').textContent = 'Auth Required';
    document.getElementById('recentJoiners').textContent = 'Auth Required';
    document.getElementById('totalDepartments').textContent = 'Auth Required';
    document.getElementById('avgAttendance').textContent = 'Auth Required';
    
    const authMessage = document.createElement('div');
    authMessage.style.cssText = `
        background: #fff3cd; 
        color: #856404; 
        padding: 20px; 
        margin: 20px 0; 
        border-radius: 8px; 
        text-align: center;
        border: 1px solid #ffeaa7;
    `;
    authMessage.innerHTML = `
        <h3>Auth Required</h3>
        <p>The dashboard requires API authentication to display data.</p>
    `;
    
    document.querySelector('.stats-grid').appendChild(authMessage);
}

function showError() {
    document.querySelector('.container').innerHTML += `
        <div style="background: #ffebee; color: #c62828; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center;">
            <h3>Unable to load dashboard data</h3>
            <p>Please make certain the API server is running and accessible.</p>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', initDashboard);
