/**
 * SSPU Campus Navigator - Admin Dashboard Logic
 * Requirement 8: Add/Edit/Delete Facilities, Form Validation, Interactive Map Picker,
 * Path Graph Management, Audit Log Inspection.
 */

(function () {
  'use strict';

  const state = {
    user: null,
    facilities: [],
    categories: [],
    buildings: [],
    nodes: [],
    edges: [],
    auditLogs: [],
    searchQuery: '',
    categoryFilter: 'all',
    pickedCoords: { x: null, y: null }
  };

  // Base SVG markup template for maps (Authentic SSPU Scale Model Top View)
  const baseMapSvgContent = `
    <image href="/static/img/campus_map_base.webp" x="0" y="0" width="1000" height="563" preserveAspectRatio="none"/>
    <rect width="1000" height="563" fill="rgba(5, 7, 10, 0.28)"/>
    <!-- Buildings Outlines for Visual Reference -->
    <polygon points="520,455 640,455 640,530 520,530" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="580" y="525" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">MAIN GATE</text>
    <polygon points="630,295 735,295 735,385 630,385" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="682" y="325" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">ADMIN</text>
    <polygon points="525,120 625,120 625,185 525,185" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="575" y="142" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">LIBRARY</text>
    <polygon points="335,315 445,315 445,405 335,405" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="390" y="345" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">AUDITORIUM</text>
    <polygon points="560,260 645,260 645,325 560,325" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="602" y="280" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">CAFETERIA</text>
    <polygon points="305,140 415,140 415,245 305,245" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="360" y="162" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">ENGG (A)</text>
    <polygon points="485,55 595,55 595,135 485,135" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="540" y="78" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">COMPUTING (B)</text>
    <polygon points="780,175 915,175 915,275 780,275" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="848" y="198" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">WORKSHOPS (C)</text>
    <polygon points="120,165 225,165 225,275 120,275" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="172" y="195" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">HOSTELS</text>
    <polygon points="190,335 285,335 285,415 190,415" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="238" y="360" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">HEALTH CTR</text>
    <polygon points="755,365 915,365 915,485 755,485" fill="none" stroke="rgba(201,162,74,0.4)" stroke-width="1.5"/>
    <text x="835" y="392" fill="#dfe7e0" font-size="8.5" font-weight="700" text-anchor="middle">SPORTS</text>
  `;

  async function checkAuth() {
    try {
      const res = await fetch('/api/me').then(r => r.json());
      if (!res.authenticated) {
        window.location.href = '/admin/login';
        return false;
      }
      state.user = res.username;
      document.getElementById('admin-username-label').textContent = res.username;
      return true;
    } catch (e) {
      window.location.href = '/admin/login';
      return false;
    }
  }

  async function init() {
    const isAuthed = await checkAuth();
    if (!isAuthed) return;

    setupTabs();
    setupEventListeners();
    await loadData();
  }

  // -------------------------------------------------------------
  // Data Loading
  // -------------------------------------------------------------
  async function loadData() {
    try {
      const [facRes, catRes, bldRes, pathRes, auditRes] = await Promise.all([
        fetch('/api/facilities').then(r => r.json()),
        fetch('/api/categories').then(r => r.json()),
        fetch('/api/buildings').then(r => r.json()),
        fetch('/api/paths').then(r => r.json()),
        fetch('/api/audit').then(r => r.json())
      ]);

      if (facRes.success) state.facilities = facRes.facilities;
      if (catRes.success) state.categories = catRes.categories;
      if (bldRes.success) state.buildings = bldRes.buildings;
      if (pathRes.success) {
        state.nodes = pathRes.nodes;
        state.edges = pathRes.edges;
      }
      if (auditRes.success) state.auditLogs = auditRes.logs;

      populateCategoryFilter();
      populateFormDropdowns();
      renderFacilitiesTable();
      renderPathGraphView();
      renderAuditTable();
    } catch (err) {
      console.error('Error loading admin data:', err);
      showToast('Error fetching data');
    }
  }

  function setupTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-tab');
        document.querySelectorAll('.tab-btn').forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        const targetEl = document.getElementById(targetId);
        if (targetEl) targetEl.classList.add('active');

        if (targetId === 'tab-paths') {
          renderPathGraphView();
        } else if (targetId === 'tab-audit') {
          refreshAuditLogs();
        }
      });
    });
  }

  // -------------------------------------------------------------
  // Facilities Table & Management
  // -------------------------------------------------------------
  function populateCategoryFilter() {
    const sel = document.getElementById('admin-category-filter');
    sel.innerHTML = '<option value="all">All Categories</option>';
    state.categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.name;
      opt.textContent = c.name;
      sel.appendChild(opt);
    });
  }

  function populateFormDropdowns() {
    const bldSel = document.getElementById('facility-building');
    bldSel.innerHTML = '';
    state.buildings.forEach(b => {
      const opt = document.createElement('option');
      opt.value = b;
      opt.textContent = b;
      bldSel.appendChild(opt);
    });

    const nodeSel = document.getElementById('facility-node');
    nodeSel.innerHTML = '<option value="">Nearest Available Node</option>';
    state.nodes.forEach(n => {
      const opt = document.createElement('option');
      opt.value = n.id;
      opt.textContent = `${n.id} (${n.name})`;
      nodeSel.appendChild(opt);
    });

    const edgeFrom = document.getElementById('edge-from-select');
    const edgeTo = document.getElementById('edge-to-select');
    edgeFrom.innerHTML = '';
    edgeTo.innerHTML = '';
    state.nodes.forEach(n => {
      const opt1 = document.createElement('option');
      opt1.value = n.id;
      opt1.textContent = `${n.id}: ${n.name}`;
      edgeFrom.appendChild(opt1);

      const opt2 = document.createElement('option');
      opt2.value = n.id;
      opt2.textContent = `${n.id}: ${n.name}`;
      edgeTo.appendChild(opt2);
    });
  }

  function renderFacilitiesTable() {
    const tbody = document.getElementById('facilities-table-body');
    tbody.innerHTML = '';

    const q = state.searchQuery.trim().toLowerCase();
    const cat = state.categoryFilter.toLowerCase();

    const filtered = state.facilities.filter(f => {
      const matchesQ = !q || (
        f.name.toLowerCase().includes(q) ||
        f.building.toLowerCase().includes(q) ||
        f.floor.toLowerCase().includes(q) ||
        f.category.toLowerCase().includes(q)
      );
      const matchesCat = cat === 'all' || f.category.toLowerCase() === cat;
      return matchesQ && matchesCat;
    });

    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--muted); padding: 24px;">No matching facilities found.</td></tr>';
      return;
    }

    filtered.forEach(f => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-family: monospace; color: var(--bone-dim);">${f.id}</td>
        <td><strong>${escapeHTML(f.name)}</strong></td>
        <td><span class="badge-tag">${escapeHTML(f.category)}</span></td>
        <td>${escapeHTML(f.building)}</td>
        <td>${escapeHTML(f.floor)}</td>
        <td style="font-size: 11px; color: var(--bone-dim);">${escapeHTML(f.operating_hours)}</td>
        <td style="font-family: monospace; font-size: 11px;">(${f.x}, ${f.y})</td>
        <td>
          <div class="table-actions">
            <button type="button" class="btn-action-edit edit-fac-btn" data-id="${f.id}">Edit</button>
            <button type="button" class="btn-action-del del-fac-btn" data-id="${f.id}" data-name="${escapeHTML(f.name)}">Delete</button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Wire action buttons
    document.querySelectorAll('.edit-fac-btn').forEach(b => {
      b.addEventListener('click', () => openEditModal(parseInt(b.getAttribute('data-id'), 10)));
    });

    document.querySelectorAll('.del-fac-btn').forEach(b => {
      b.addEventListener('click', () => {
        const id = parseInt(b.getAttribute('data-id'), 10);
        const name = b.getAttribute('data-name');
        deleteFacility(id, name);
      });
    });
  }

  // -------------------------------------------------------------
  // Add & Edit Facility Modal Logic
  // -------------------------------------------------------------
  const modal = document.getElementById('facility-modal');
  const form = document.getElementById('facility-form');
  const modalTitle = document.getElementById('facility-modal-title');
  const modalErr = document.getElementById('modal-error-alert');

  function openAddModal() {
    form.reset();
    document.getElementById('facility-id').value = '';
    modalTitle.textContent = 'Add New Facility';
    modalErr.style.display = 'none';
    modal.classList.add('active');
  }

  function openEditModal(id) {
    const f = state.facilities.find(item => item.id === id);
    if (!f) return;

    form.reset();
    document.getElementById('facility-id').value = f.id;
    document.getElementById('facility-name').value = f.name;
    document.getElementById('facility-category').value = f.category;
    document.getElementById('facility-building').value = f.building;
    document.getElementById('facility-floor').value = f.floor;
    document.getElementById('facility-hours').value = f.operating_hours;
    document.getElementById('facility-desc').value = f.description;
    document.getElementById('facility-contact').value = f.contact || '';
    document.getElementById('facility-node').value = f.node_id || '';
    document.getElementById('facility-x').value = f.x;
    document.getElementById('facility-y').value = f.y;

    modalTitle.textContent = `Edit Facility #${f.id} — ${f.name}`;
    modalErr.style.display = 'none';
    modal.classList.add('active');
  }

  function closeFacilityModal() {
    modal.classList.remove('active');
  }

  async function handleFacilitySubmit(e) {
    e.preventDefault();
    modalErr.style.display = 'none';

    const id = document.getElementById('facility-id').value;
    const name = document.getElementById('facility-name').value.trim();
    const category = document.getElementById('facility-category').value;
    const building = document.getElementById('facility-building').value;
    const floor = document.getElementById('facility-floor').value;
    const operating_hours = document.getElementById('facility-hours').value.trim();
    const description = document.getElementById('facility-desc').value.trim();
    const contact = document.getElementById('facility-contact').value.trim();
    const node_id = document.getElementById('facility-node').value;
    const x = parseFloat(document.getElementById('facility-x').value);
    const y = parseFloat(document.getElementById('facility-y').value);

    // Validation
    if (!name || !operating_hours || !description || isNaN(x) || isNaN(y)) {
      modalErr.textContent = 'Please fill out all required fields with valid values.';
      modalErr.style.display = 'block';
      return;
    }

    if (x < 0 || x > 1000 || y < 0 || y > 700) {
      modalErr.textContent = 'Coordinates must be within X: 0-1000 and Y: 0-700.';
      modalErr.style.display = 'block';
      return;
    }

    const payload = {
      name, category, building, floor,
      operating_hours, description, contact, node_id, x, y
    };

    const isEdit = Boolean(id);
    const url = isEdit ? `/api/facilities/${id}` : '/api/facilities';
    const method = isEdit ? 'PUT' : 'POST';

    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(r => r.json());

      if (res.success) {
        showToast(isEdit ? `Facility updated: ${name}` : `Facility created: ${name}`);
        closeFacilityModal();
        await loadData();
      } else {
        modalErr.textContent = res.error || 'Failed to save facility.';
        modalErr.style.display = 'block';
      }
    } catch (err) {
      modalErr.textContent = 'Network or server error while saving.';
      modalErr.style.display = 'block';
    }
  }

  async function deleteFacility(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}" (ID #${id})?\nThis action cannot be undone.`)) {
      return;
    }

    try {
      const res = await fetch(`/api/facilities/${id}`, { method: 'DELETE' }).then(r => r.json());
      if (res.success) {
        showToast(`Deleted facility: ${name}`);
        await loadData();
      } else {
        showToast(res.error || 'Could not delete facility');
      }
    } catch (err) {
      showToast('Error deleting facility');
    }
  }

  // -------------------------------------------------------------
  // Interactive Map Location Picker
  // -------------------------------------------------------------
  const pickerModal = document.getElementById('map-picker-modal');
  const pickerContainer = document.getElementById('picker-svg-container');
  const coordLabel = document.getElementById('picker-selected-coord-label');

  function openMapPicker() {
    pickerContainer.innerHTML = `
      <svg id="picker-svg" viewBox="0 0 1000 563" style="width: 100%; height: 100%;">
        ${baseMapSvgContent}
        <g id="picker-pin-layer"></g>
      </svg>
    `;

    const initialX = parseFloat(document.getElementById('facility-x').value);
    const initialY = parseFloat(document.getElementById('facility-y').value);

    if (!isNaN(initialX) && !isNaN(initialY)) {
      setPickerPin(initialX, initialY);
    } else {
      coordLabel.textContent = 'Selected: (Click map)';
      state.pickedCoords = { x: null, y: null };
    }

    const svg = document.getElementById('picker-svg');
    svg.addEventListener('click', (e) => {
      const rect = svg.getBoundingClientRect();
      const clickX = Math.round(((e.clientX - rect.left) / rect.width) * 1000);
      const clickY = Math.round(((e.clientY - rect.top) / rect.height) * 563);

      const boundedX = Math.max(10, Math.min(990, clickX));
      const boundedY = Math.max(10, Math.min(550, clickY));

      setPickerPin(boundedX, boundedY);
    });

    pickerModal.classList.add('active');
  }

  function setPickerPin(x, y) {
    state.pickedCoords = { x, y };
    coordLabel.textContent = `Selected: X=${x}, Y=${y}`;

    const layer = document.getElementById('picker-pin-layer');
    if (layer) {
      layer.innerHTML = `
        <circle cx="${x}" cy="${y}" r="16" fill="rgba(224, 35, 28, 0.25)" stroke="var(--vermilion)" stroke-width="1.5"/>
        <circle cx="${x}" cy="${y}" r="6" fill="var(--vermilion)" stroke="#fff" stroke-width="2"/>
        <line x1="${x - 12}" y1="${y}" x2="${x + 12}" y2="${y}" stroke="var(--gold)" stroke-width="1.5"/>
        <line x1="${x}" y1="${y - 12}" x2="${x}" y2="${y + 12}" stroke="var(--gold)" stroke-width="1.5"/>
      `;
    }
  }

  function confirmPickedCoords() {
    if (state.pickedCoords.x !== null && state.pickedCoords.y !== null) {
      document.getElementById('facility-x').value = state.pickedCoords.x;
      document.getElementById('facility-y').value = state.pickedCoords.y;
      showToast(`Location set: (${state.pickedCoords.x}, ${state.pickedCoords.y})`);
    }
    pickerModal.classList.remove('active');
  }

  // -------------------------------------------------------------
  // Path Graph Manager View
  // -------------------------------------------------------------
  function renderPathGraphView() {
    const svg = document.getElementById('paths-svg-map');
    if (!svg) return;

    let pathsLinesHtml = '';
    state.edges.forEach(e => {
      pathsLinesHtml += `
        <line x1="${e.from_x}" y1="${e.from_y}" x2="${e.to_x}" y2="${e.to_y}" 
              stroke="#e0231c" stroke-width="2.5" stroke-dasharray="4,2" opacity="0.85"/>
      `;
    });

    let nodesHtml = '';
    state.nodes.forEach(n => {
      nodesHtml += `
        <g transform="translate(${n.x}, ${n.y})">
          <circle cx="0" cy="0" r="5" fill="#4a90e2" stroke="#fff" stroke-width="1.5"/>
          <text x="0" y="-8" fill="#dfe7e0" font-size="8" font-family="Onest" text-anchor="middle">${n.id}</text>
        </g>
      `;
    });

    svg.innerHTML = `
      ${baseMapSvgContent}
      <g id="admin-edges-layer">${pathsLinesHtml}</g>
      <g id="admin-nodes-layer">${nodesHtml}</g>
    `;

    // Render edges table
    const tbody = document.getElementById('edges-table-body');
    tbody.innerHTML = '';
    document.getElementById('edges-count').textContent = state.edges.length;

    state.edges.forEach(e => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-size: 11px;">${e.from_node} &rarr; ${e.to_node}</td>
        <td style="font-family: monospace;">${e.distance}m</td>
        <td style="text-align: right;">
          <button type="button" class="btn-action-del del-edge-btn" data-id="${e.id}">&times;</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    document.querySelectorAll('.del-edge-btn').forEach(b => {
      b.addEventListener('click', async () => {
        const id = parseInt(b.getAttribute('data-id'), 10);
        await deleteEdge(id);
      });
    });
  }

  async function deleteEdge(edgeId) {
    if (!confirm(`Delete path connection #${edgeId}?`)) return;
    try {
      const res = await fetch(`/api/paths/edges/${edgeId}`, { method: 'DELETE' }).then(r => r.json());
      if (res.success) {
        showToast('Path connection removed');
        await loadData();
      }
    } catch (err) {
      showToast('Error removing path edge');
    }
  }

  async function handleAddEdgeSubmit(e) {
    e.preventDefault();
    const from_node = document.getElementById('edge-from-select').value;
    const to_node = document.getElementById('edge-to-select').value;
    const distance = parseFloat(document.getElementById('edge-dist-input').value);
    const description = document.getElementById('edge-desc-input').value.trim();

    if (from_node === to_node) {
      showToast('Cannot connect a node to itself.');
      return;
    }

    try {
      const res = await fetch('/api/paths/edges', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_node, to_node, distance, description })
      }).then(r => r.json());

      if (res.success) {
        showToast(`Connected ${from_node} &harr; ${to_node}`);
        document.getElementById('add-edge-form').reset();
        await loadData();
      } else {
        showToast(res.error || 'Failed to add edge');
      }
    } catch (err) {
      showToast('Error saving path connection');
    }
  }

  // -------------------------------------------------------------
  // Audit Logs
  // -------------------------------------------------------------
  function renderAuditTable() {
    const tbody = document.getElementById('audit-table-body');
    tbody.innerHTML = '';

    if (state.auditLogs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--muted); padding: 20px;">No audit logs recorded yet.</td></tr>';
      return;
    }

    state.auditLogs.forEach(log => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-family: monospace; color: var(--bone-dim);">${log.id}</td>
        <td><span class="badge-tag" style="border-color: var(--gold); color: var(--gold);">${escapeHTML(log.action)}</span></td>
        <td style="font-size: 11px;">${escapeHTML(log.details)}</td>
        <td style="font-family: monospace; font-size: 11px; color: var(--bone-dim);">${escapeHTML(log.timestamp)}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  async function refreshAuditLogs() {
    try {
      const res = await fetch('/api/audit').then(r => r.json());
      if (res.success) {
        state.auditLogs = res.logs;
        renderAuditTable();
        showToast('Audit records updated');
      }
    } catch (e) {
      showToast('Error refreshing audit logs');
    }
  }

  // -------------------------------------------------------------
  // Event Listeners
  // -------------------------------------------------------------
  function setupEventListeners() {
    // Search & Filter
    document.getElementById('admin-facility-search').addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      renderFacilitiesTable();
    });

    document.getElementById('admin-category-filter').addEventListener('change', (e) => {
      state.categoryFilter = e.target.value;
      renderFacilitiesTable();
    });

    // Facility Modal
    document.getElementById('btn-open-add-modal').addEventListener('click', openAddModal);
    document.getElementById('facility-modal-close').addEventListener('click', closeFacilityModal);
    document.getElementById('btn-cancel-facility').addEventListener('click', closeFacilityModal);
    form.addEventListener('submit', handleFacilitySubmit);

    // Map Picker
    document.getElementById('btn-trigger-map-picker').addEventListener('click', openMapPicker);
    document.getElementById('map-picker-close').addEventListener('click', () => pickerModal.classList.remove('active'));
    document.getElementById('btn-confirm-coords').addEventListener('click', confirmPickedCoords);

    // Path edge form
    document.getElementById('add-edge-form').addEventListener('submit', handleAddEdgeSubmit);
    document.getElementById('edge-from-select').addEventListener('change', autoCalculateEdgeDist);
    document.getElementById('edge-to-select').addEventListener('change', autoCalculateEdgeDist);

    // Audit refresh
    document.getElementById('btn-refresh-audit').addEventListener('click', refreshAuditLogs);

    // Logout
    document.getElementById('admin-logout-btn').addEventListener('click', async () => {
      await fetch('/api/logout', { method: 'POST' });
      window.location.href = '/admin/login';
    });
  }

  function autoCalculateEdgeDist() {
    const uId = document.getElementById('edge-from-select').value;
    const vId = document.getElementById('edge-to-select').value;
    if (uId && vId && uId !== vId) {
      const n1 = state.nodes.find(n => n.id === uId);
      const n2 = state.nodes.find(n => n.id === vId);
      if (n1 && n2) {
        const dx = n1.x - n2.x;
        const dy = n1.y - n2.y;
        const dist = Math.round(Math.hypot(dx, dy) * 0.85 * 10) / 10;
        document.getElementById('edge-dist-input').value = dist;
      }
    }
  }

  function showToast(msg) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 2800);
  }

  function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
