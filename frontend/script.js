let currentFile = null;
let currentFileType = null;
let violationsChartInstance = null;

// ================= NAVIGATION & VIEWS =================
function switchTab(tab) {
    document.getElementById('login-form').classList.toggle('active', tab === 'login');
    document.getElementById('signup-form').classList.toggle('active', tab === 'signup');
    document.getElementById('login-tab-btn').classList.toggle('active', tab === 'login');
    document.getElementById('signup-tab-btn').classList.toggle('active', tab === 'signup');
}

function switchView(viewId, btnElement) {
    document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    
    document.getElementById(viewId).classList.add('active');
    btnElement.classList.add('active');

    if (viewId === 'dashboard-view') {
        loadDashboardMetrics();
        loadViolationsTable();
    }
}

function openDashboard() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('upload-section').style.display = 'flex';
    loadDashboardMetrics();
    loadViolationsTable();
}

function logout() {
    document.getElementById('upload-section').style.display = 'none';
    document.getElementById('auth-section').style.display = 'flex';
}

// ================= AUTHENTICATION =================
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById('user-display-name').innerText = data.user?.name || 'Safety Officer';
            openDashboard();
        } else {
            alert(data.message || 'Authentication failed.');
        }
    } catch (err) {
        alert('Server unreachable.');
    }
});

document.getElementById('signup-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fullName = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    try {
        const res = await fetch('/api/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: fullName, email, password })
        });
        const data = await res.json();
        if (data.success) {
            alert("Account registered! Signing into workplace suite...");
            openDashboard();
        } else {
            alert(data.message || 'Signup failed.');
        }
    } catch (err) {
        alert('Could not complete registration.');
    }
});

// ================= MODULE 6: DASHBOARD & REPORTING =================
async function loadDashboardMetrics() {
    try {
        const res = await fetch('/api/dashboard/metrics');
        const data = await res.json();
        if (!data.success) return;

        // KPI Bindings
        document.getElementById('kpi-compliance').innerText = `${data.kpis.compliance_percentage}%`;
        document.getElementById('kpi-critical').innerText = data.kpis.critical_violations;
        document.getElementById('kpi-total').innerText = data.kpis.total_violations;
        document.getElementById('kpi-open').innerText = data.kpis.open_violations;
        document.getElementById('kpi-resolved').innerText = data.kpis.resolved_violations;
        document.getElementById('kpi-resolution').innerText = `${data.kpis.resolution_rate}%`;

        // Render Chart.js
        renderViolationsChart(data.by_type);

        // Render Department Scoreboard
        const deptBoard = document.getElementById('deptLeaderboard');
        deptBoard.innerHTML = data.department_scores.map(d => `
            <div class="leaderboard-item">
                <span><strong>${d.department}</strong></span>
                <span class="leaderboard-score">${d.score}% Score • ${d.status}</span>
            </div>
        `).join('');

    } catch (e) {
        console.error("Dashboard metric error:", e);
    }
}

function renderViolationsChart(typeData) {
    const ctx = document.getElementById('violationsTypeChart').getContext('2d');
    if (violationsChartInstance) violationsChartInstance.destroy();

    const labels = Object.keys(typeData);
    const counts = Object.values(typeData);

    violationsChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.length ? labels : ['No Data'],
            datasets: [{
                label: 'Violations Detected',
                data: counts.length ? counts : [0],
                backgroundColor: '#6366f1',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#1e2638' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
            }
        }
    });
}

async function loadViolationsTable() {
    const severity = document.getElementById('filterSeverity').value;
    const status = document.getElementById('filterStatus').value;

    try {
        const res = await fetch(`/api/dashboard/violations?severity=${severity}&status=${status}`);
        const data = await res.json();
        const tbody = document.getElementById('violationsTableBody');
        tbody.innerHTML = '';

        if (!data.violations || data.violations.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;color:#94a3b8;">No matching violation logs.</td></tr>`;
            return;
        }

        data.violations.forEach(v => {
            const sevBadge = v.severity === 'Critical' ? 'badge-critical' : 'badge-high';
            const statBadge = v.status === 'Resolved' ? 'badge-resolved' : 'badge-open';
            tbody.innerHTML += `
                <tr>
                    <td>#${v.id}</td>
                    <td>${v.timestamp}</td>
                    <td><strong>${v.violation_type}</strong></td>
                    <td>${v.location}</td>
                    <td>${v.department}</td>
                    <td><span class="badge ${sevBadge}">${v.severity}</span></td>
                    <td><span class="badge ${statBadge}">${v.status}</span></td>
                    <td>
                        ${v.status !== 'Resolved' ? 
                            `<button class="btn btn-secondary" style="padding:4px 8px;font-size:11px;" onclick="updateViolationStatus(${v.id}, 'Resolved')">Resolve</button>` : 
                            `<span style="color:#10b981;font-size:12px;">✓ Completed</span>`}
                    </td>
                </tr>
            `;
        });
    } catch (e) {
        console.error("Table fetch error:", e);
    }
}

async function updateViolationStatus(id, newStatus) {
    await fetch('/api/dashboard/update-status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status: newStatus })
    });
    loadDashboardMetrics();
    loadViolationsTable();
}

// ================= MODULE 1 & 2: LIVE VISION & RAG =================
function handleFileSelect(type) {
    const input = document.getElementById(`${type === 'document' ? 'doc' : type}Input`);
    if (input?.files && input.files[0]) {
        currentFile = input.files[0];
        currentFileType = type;
        document.getElementById('fileName').innerText = currentFile.name;
        document.getElementById('fileMeta').innerText = `${type.toUpperCase()} • ${(currentFile.size / (1024 * 1024)).toFixed(2)} MB`;
        document.getElementById('clearBtn').style.display = 'block';
    }
}

function clearSelectedFile() {
    currentFile = null;
    document.getElementById('fileName').innerText = 'No file chosen';
    document.getElementById('fileMeta').innerText = 'Select an image, video, or document';
    document.getElementById('clearBtn').style.display = 'none';
    document.getElementById('previewStage').innerHTML = `
        <div class="placeholder-content">
            <i class="fa-solid fa-eye-slash fa-2x"></i>
            <h3>No Media Selected</h3>
            <p>Upload an image or video to inspect safety violations.</p>
        </div>
    `;
}

function renderPreview() {
    if (!currentFile) return alert('Select a file first.');
    const stage = document.getElementById('previewStage');
    const url = URL.createObjectURL(currentFile);
    if (currentFileType === 'image') {
        stage.innerHTML = `<img src="${url}" class="preview-media" alt="preview">`;
    } else if (currentFileType === 'video') {
        stage.innerHTML = `<video src="${url}" class="preview-media" controls autoplay loop muted></video>`;
    } else {
        stage.innerHTML = `<div class="placeholder-content"><h3>Document Ready</h3><p>${currentFile.name}</p></div>`;
    }
}

async function analyzeMedia() {
    if (!currentFile) return alert('Please select a file.');
    const stage = document.getElementById('previewStage');
    stage.innerHTML = `<div class="placeholder-content"><h3>Analyzing with YOLO & RAG...</h3></div>`;

    const formData = new FormData();
    formData.append('file', currentFile);

    const endpoint = currentFileType === 'document' ? '/api/process-document' : '/api/analyze';
    const res = await fetch(endpoint, { method: 'POST', body: formData });
    const data = await res.json();

    if (data.success) {
        if (currentFileType === 'image') {
            stage.innerHTML = `<img src="${data.media_url}" class="preview-media">`;
        } else if (currentFileType === 'video') {
            stage.innerHTML = `<video src="${data.media_url}" class="preview-media" controls autoplay loop muted></video>`;
        }
        document.getElementById('detectionDetails').innerHTML = (data.detections || []).map(d => `<span class="badge badge-high">${d}</span>`).join(' ');
        loadDashboardMetrics();
    } else {
        alert(data.message || 'Analysis failed.');
    }
}

// ================= MODULE 3 & 4 =================
async function runCorrelation() {
    const res = await fetch('/api/correlate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            detection: document.getElementById('correlationDetection').value,
            rules: document.getElementById('correlationRules').value
        })
    });
    const data = await res.json();
    document.getElementById('correlationResult').textContent = JSON.stringify(data.result, null, 2);
}

async function askSafetyQuestion() {
    const question = document.getElementById('safetyQuestion').value.trim();
    if (!question) return alert('Enter question.');
    const res = await fetch('/api/safety-qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    });
    const data = await res.json();
    document.getElementById('qaResult').textContent = data.answer + "\n\nEvidence Sources: " + (data.evidence || []).join(', ');
}

// ================= MODULE 5 =================
async function runInvestigation() {
    const query = document.getElementById('investigationQuery').value.trim();
    if (!query) return alert('Enter investigation details.');
    const status = document.getElementById('investigationStatus');
    status.innerHTML = `<strong>Running LangGraph Investigation Agents...</strong>`;

    const res = await fetch('/api/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
    });
    const data = await res.json();
    status.innerHTML = `<strong>Investigation Completed!</strong>`;
    document.getElementById('reportContent').textContent = data.report;
    document.getElementById('investigationReport').style.display = 'block';
}

function approveInvestigation() {
    document.getElementById('reviewBadge').className = 'badge badge-resolved';
    document.getElementById('reviewBadge').innerText = '✓ Approved & Signed-off';
    alert('Investigation Audit Report officially approved.');
}

function rejectInvestigation() {
    prompt('Enter revision comments:');
    document.getElementById('reviewBadge').className = 'badge badge-critical';
    document.getElementById('reviewBadge').innerText = 'Revision Requested';
}