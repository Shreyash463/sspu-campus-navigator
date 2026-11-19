/**
 * SSPU Campus Navigator - Interactive Application Logic
 * Requirements 1 to 7: Directory, Filtering, Search, SVG Map Pan/Zoom,
 * Facility Details with Live Open/Closed Status, Dijkstra Animated Route Finder.
 */

(function () {
  'use strict';

  // Application State
  const state = {
    facilities: [],
    categories: [],
    buildings: [],
    selectedFacility: null,
    searchQuery: '',
    categoryFilter: 'all',
    buildingFilter: 'all',
    route: { fromId: null, toId: null, data: null },
    mapTransform: { x: 0, y: 0, scale: 1.0 },
    isDragging: false,
    dragStart: { x: 0, y: 0 },
    recentlyViewed: []
  };

  // Color mapping for categories
  const categoryColorMap = {
    'academic': '#ff5a3c',
    'laboratory': '#e0231c',
    'library': '#c9a24a',
    'administrative': '#4a90e2',
    'cafeteria': '#50e3c2',
    'auditorium & events': '#b8e986',
    'sports & recreation': '#bd10e0',
    'student services': '#f5a623'
  };

  function getCategoryColor(cat) {
    if (!cat) return '#c9a24a';
    return categoryColorMap[cat.toLowerCase()] || '#c9a24a';
  }

  // DOM Elements
  const els = {
    searchInput: document.getElementById('facility-search-input'),
    searchClearBtn: document.getElementById('search-clear-btn'),
    buildingSelect: document.getElementById('building-filter-select'),
    categoryContainer: document.getElementById('category-chips-container'),
    resultsCount: document.getElementById('results-count-text'),
    resetFiltersBtn: document.getElementById('reset-filters-btn'),
    facilitiesList: document.getElementById('facilities-list-container'),
    popularPills: document.getElementById('popular-places-pills'),
    recentPills: document.getElementById('recently-viewed-pills'),
    svgMap: document.getElementById('campus-svg-map'),
    mapViewport: document.getElementById('map-viewport'),
    mapMarkersLayer: document.getElementById('map-markers-layer'),
    mapRouteLayer: document.getElementById('map-route-layer'),
    mapTooltipLayer: document.getElementById('map-tooltip-layer'),
    zoomInBtn: document.getElementById('map-zoom-in'),
    zoomOutBtn: document.getElementById('map-zoom-out'),
    resetViewBtn: document.getElementById('map-reset-view'),
    legendItems: document.getElementById('legend-items'),
    // Details
    detailCard: document.getElementById('detail-card-panel'),
    detailCloseBtn: document.getElementById('detail-close-btn'),
    detailCategoryBadge: document.getElementById('detail-category-badge'),
    detailStatusText: document.getElementById('detail-status-text'),
    detailLiveStatus: document.getElementById('detail-live-status'),
    detailName: document.getElementById('detail-name'),
    detailBuilding: document.getElementById('detail-building'),
    detailFloor: document.getElementById('detail-floor'),
    detailHours: document.getElementById('detail-hours'),
    detailContact: document.getElementById('detail-contact'),
    detailContactRow: document.getElementById('detail-contact-row'),
    detailDesc: document.getElementById('detail-description'),
    btnDirectionsTo: document.getElementById('btn-directions-to'),
    btnDirectionsFrom: document.getElementById('btn-directions-from'),
    // Route Drawer
    routeDrawer: document.getElementById('route-drawer-panel'),
    navRouteToggle: document.getElementById('nav-route-toggle'),
    routeCloseBtn: document.getElementById('route-close-btn'),
    routeFromSelect: document.getElementById('route-from-select'),
    routeToSelect: document.getElementById('route-to-select'),
    routeSummaryCard: document.getElementById('route-summary-card'),
    routeDistVal: document.getElementById('route-dist-val'),
    routeTimeVal: document.getElementById('route-time-val'),
    routeStepsContainer: document.getElementById('route-steps-container'),
    // Ask Campus Modal
    openAskBtn: document.getElementById('open-ask-btn'),
    askModal: document.getElementById('ask-ai-modal'),
    closeAskBtn: document.getElementById('close-ask-modal-btn'),
    askForm: document.getElementById('ask-ai-form'),
    askInput: document.getElementById('ask-question-input'),
    askAnswerBox: document.getElementById('ask-answer-box'),
    askAnswerText: document.getElementById('ask-answer-text'),
    askMatchedPills: document.getElementById('ask-matched-pills'),
    // Toast & Cursor
    toastContainer: document.getElementById('toast-container'),
    customCursor: document.getElementById('custom-cursor')
  };

  // -------------------------------------------------------------
  // Data Fetching & Initialization
  // -------------------------------------------------------------
  async function init() {
    setupCustomCursor();
    setupPanZoom();
    loadRecentlyViewed();

    try {
      const [facRes, catRes, bldRes] = await Promise.all([
        fetch('/api/facilities').then(r => r.json()),
        fetch('/api/categories').then(r => r.json()),
        fetch('/api/buildings').then(r => r.json())
      ]);

      if (facRes.success) state.facilities = facRes.facilities;
      if (catRes.success) state.categories = catRes.categories;
      if (bldRes.success) state.buildings = bldRes.buildings;

      populateCategoryChips();
      populateBuildingSelect();
      populateRouteSelects();
      populateLegend();
      populatePopularPlaces();
      renderFacilitiesList();
      renderMarkers();
      updateRecentPillsUI();

      // Check URL query params for deep-link selection or route
      const params = new URLSearchParams(window.location.search);
      if (params.get('id')) {
        const targetId = parseInt(params.get('id'), 10);
        selectFacility(targetId, true);
      } else if (params.get('from') && params.get('to')) {
        state.route.fromId = parseInt(params.get('from'), 10);
        state.route.toId = parseInt(params.get('to'), 10);
        els.routeFromSelect.value = state.route.fromId;
        els.routeToSelect.value = state.route.toId;
        openRouteDrawer();
        calculateRoute();
      }
    } catch (err) {
      console.error('Initialization error:', err);
      showToast('Error loading campus data');
    }

    setupEventListeners();
  }

  // -------------------------------------------------------------
  // Custom Ring Cursor
  // -------------------------------------------------------------
  function setupCustomCursor() {
    if (!els.customCursor) return;
    window.addEventListener('mousemove', (e) => {
      els.customCursor.style.left = e.clientX + 'px';
      els.customCursor.style.top = e.clientY + 'px';
    });

    document.querySelectorAll('a, button, input, select, .chip, .facility-card-item, .marker-pin').forEach(elem => {
      elem.addEventListener('mouseenter', () => els.customCursor.classList.add('active'));
      elem.addEventListener('mouseleave', () => els.customCursor.classList.remove('active'));
    });
  }

  // -------------------------------------------------------------
  // Map View Pan & Zoom
  // -------------------------------------------------------------
  function setupPanZoom() {
    let viewBox = { x: 0, y: 0, w: 1000, h: 700 };

    function updateViewBox() {
      els.svgMap.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`);
    }

    // Zoom Buttons
    els.zoomInBtn.addEventListener('click', () => {
      zoomAtCenter(0.8);
    });

    els.zoomOutBtn.addEventListener('click', () => {
      zoomAtCenter(1.25);
    });

    els.resetViewBtn.addEventListener('click', () => {
      viewBox = { x: 0, y: 0, w: 1000, h: 700 };
      updateViewBox();
      showToast('Map view reset');
    });

    function zoomAtCenter(factor) {
      const newW = Math.max(250, Math.min(1400, viewBox.w * factor));
      const newH = Math.max(175, Math.min(980, viewBox.h * factor));
      const dx = (viewBox.w - newW) / 2;
      const dy = (viewBox.h - newH) / 2;
      viewBox.x += dx;
      viewBox.y += dy;
      viewBox.w = newW;
      viewBox.h = newH;
      updateViewBox();
    }

    // Mouse Drag Panning
    let isPanning = false;
    let startPoint = { x: 0, y: 0 };

    els.mapViewport.addEventListener('mousedown', (e) => {
      if (e.target.closest('.map-controls-group') || e.target.closest('.map-legend-box') || e.target.closest('.detail-card-panel') || e.target.closest('.route-drawer-panel')) return;
      isPanning = true;
      startPoint = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mousemove', (e) => {
      if (!isPanning) return;
      const rect = els.mapViewport.getBoundingClientRect();
      const scaleX = viewBox.w / rect.width;
      const scaleY = viewBox.h / rect.height;

      const dx = (e.clientX - startPoint.x) * scaleX;
      const dy = (e.clientY - startPoint.y) * scaleY;

      viewBox.x -= dx;
      viewBox.y -= dy;
      startPoint = { x: e.clientX, y: e.clientY };
      updateViewBox();
    });

    window.addEventListener('mouseup', () => { isPanning = false; });

    // Wheel Zoom
    els.mapViewport.addEventListener('wheel', (e) => {
      e.preventDefault();
      const factor = e.deltaY > 0 ? 1.15 : 0.85;
      zoomAtCenter(factor);
    }, { passive: false });

    // Smooth Pan to Target (X, Y)
    window.panMapTo = function(targetX, targetY) {
      const targetW = 600;
      const targetH = 420;
      const startX = viewBox.x;
      const startY = viewBox.y;
      const startW = viewBox.w;
      const startH = viewBox.h;

      const endX = targetX - targetW / 2;
      const endY = targetY - targetH / 2;

      const startTime = performance.now();
      const duration = 500;

      function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(1, elapsed / duration);
        const ease = 1 - Math.pow(1 - progress, 3); // ease-out cubic

        viewBox.x = startX + (endX - startX) * ease;
        viewBox.y = startY + (endY - startY) * ease;
        viewBox.w = startW + (targetW - startW) * ease;
        viewBox.h = startH + (targetH - startH) * ease;
        updateViewBox();

        if (progress < 1) {
          requestAnimationFrame(step);
        }
      }
      requestAnimationFrame(step);
    };
  }

  // -------------------------------------------------------------
  // Filter & Search Controls
  // -------------------------------------------------------------
  function populateCategoryChips() {
    els.categoryContainer.innerHTML = '';
    const allBtn = document.createElement('button');
    allBtn.type = 'button';
    allBtn.className = 'chip' + (state.categoryFilter === 'all' ? ' active' : '');
    allBtn.setAttribute('data-category', 'all');
    allBtn.textContent = 'All Facilities';
    allBtn.addEventListener('click', () => setCategoryFilter('all'));
    els.categoryContainer.appendChild(allBtn);

    state.categories.forEach(cat => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chip' + (state.categoryFilter.toLowerCase() === cat.name.toLowerCase() ? ' active' : '');
      btn.setAttribute('data-category', cat.name);

      const dot = document.createElement('span');
      dot.className = 'chip-dot';
      dot.style.backgroundColor = cat.color || getCategoryColor(cat.name);
      btn.appendChild(dot);

      const label = document.createTextNode(cat.name);
      btn.appendChild(label);

      btn.addEventListener('click', () => setCategoryFilter(cat.name));
      els.categoryContainer.appendChild(btn);
    });
  }

  function setCategoryFilter(cat) {
    state.categoryFilter = cat;
    document.querySelectorAll('#category-chips-container .chip').forEach(btn => {
      const c = btn.getAttribute('data-category');
      btn.classList.toggle('active', c.toLowerCase() === cat.toLowerCase());
    });
    applyFilters();
  }

  function populateBuildingSelect() {
    els.buildingSelect.innerHTML = '<option value="all">All Buildings (Entire Campus)</option>';
    state.buildings.forEach(bld => {
      const opt = document.createElement('option');
      opt.value = bld;
      opt.textContent = bld;
      els.buildingSelect.appendChild(opt);
    });
  }

  function populateRouteSelects() {
    const sorted = [...state.facilities].sort((a, b) => a.name.localeCompare(b.name));
    els.routeFromSelect.innerHTML = '<option value="">Choose origin...</option>';
    els.routeToSelect.innerHTML = '<option value="">Choose destination...</option>';

    sorted.forEach(f => {
      const opt1 = document.createElement('option');
      opt1.value = f.id;
      opt1.textContent = `${f.name} (${f.building})`;
      els.routeFromSelect.appendChild(opt1);

      const opt2 = document.createElement('option');
      opt2.value = f.id;
      opt2.textContent = `${f.name} (${f.building})`;
      els.routeToSelect.appendChild(opt2);
    });
  }

  function populateLegend() {
    els.legendItems.innerHTML = '';
    state.categories.forEach(cat => {
      const item = document.createElement('div');
      item.className = 'legend-item';
      item.innerHTML = `<span style="width: 8px; height: 8px; border-radius: 50%; background-color: ${cat.color || getCategoryColor(cat.name)}; flex-shrink: 0;"></span><span>${cat.name}</span>`;
      els.legendItems.appendChild(item);
    });
  }

  function populatePopularPlaces() {
    const popularNames = ['Central Library', 'Central Cafeteria & Food Court', 'Advanced AI & Cloud Computing Lab', 'University Grand Auditorium', 'Central Administrative Office', 'Athletics Track & Football Arena'];
    const populars = state.facilities.filter(f => popularNames.includes(f.name));
    
    els.popularPills.innerHTML = '';
    populars.forEach(f => {
      const pill = document.createElement('button');
      pill.type = 'button';
      pill.className = 'quick-pill';
      pill.textContent = f.name.replace(' & Food Court', '').replace(' & Football Arena', '');
      pill.addEventListener('click', () => selectFacility(f.id, true));
      els.popularPills.appendChild(pill);
    });
  }

  function applyFilters() {
    const q = state.searchQuery.trim().toLowerCase();
    const cat = state.categoryFilter.toLowerCase();
    const bld = state.buildingFilter.toLowerCase();

    const filtered = state.facilities.filter(f => {
      const matchesQ = !q || (
        f.name.toLowerCase().includes(q) ||
        f.building.toLowerCase().includes(q) ||
        f.floor.toLowerCase().includes(q) ||
        f.description.toLowerCase().includes(q) ||
        f.category.toLowerCase().includes(q)
      );
      const matchesCat = cat === 'all' || f.category.toLowerCase() === cat;
      const matchesBld = bld === 'all' || f.building.toLowerCase() === bld;
      return matchesQ && matchesCat && matchesBld;
    });

    renderFacilitiesList(filtered);
    renderMarkers(filtered);

    // Update Result count and Reset button
    const isFiltered = q !== '' || cat !== 'all' || bld !== 'all';
    els.resultsCount.textContent = `${filtered.length} of ${state.facilities.length} facilities`;
    els.resetFiltersBtn.style.display = isFiltered ? 'inline-block' : 'none';
    els.searchClearBtn.classList.toggle('visible', q.length > 0);
  }

  // -------------------------------------------------------------
  // Render Facilities List
  // -------------------------------------------------------------
  function renderFacilitiesList(list = state.facilities) {
    els.facilitiesList.innerHTML = '';

    if (list.length === 0) {
      els.facilitiesList.innerHTML = `
        <div class="empty-state">
          <h4>No facilities found</h4>
          <p>Try clearing your search query or switching category filters.</p>
        </div>
      `;
      return;
    }

    list.forEach(f => {
      const item = document.createElement('div');
      item.className = 'facility-card-item' + (state.selectedFacility && state.selectedFacility.id === f.id ? ' selected' : '');
      item.setAttribute('data-id', f.id);
      item.setAttribute('role', 'listitem');

      const color = getCategoryColor(f.category);
      const statusClass = f.is_open ? 'status-open' : 'status-closed';

      item.innerHTML = `
        <div class="facility-item-header">
          <div class="facility-item-title">${escapeHTML(f.name)}</div>
          <span class="badge-tag" style="border-color: ${color}; color: ${color};">${escapeHTML(f.category)}</span>
        </div>
        <div class="facility-item-location">
          <span>${escapeHTML(f.building)} · ${escapeHTML(f.floor)}</span>
        </div>
        <div class="facility-item-status">
          <span class="status-indicator-dot ${statusClass}"></span>
          <span style="color: ${f.is_open ? '#2ecc71' : '#e74c3c'}">${escapeHTML(f.status_badge || (f.is_open ? 'Open now' : 'Closed'))}</span>
        </div>
      `;

      item.addEventListener('click', () => selectFacility(f.id, true));
      els.facilitiesList.appendChild(item);
    });
  }

  // -------------------------------------------------------------
  // Render Map Markers
  // -------------------------------------------------------------
  function renderMarkers(list = state.facilities) {
    els.mapMarkersLayer.innerHTML = '';

    list.forEach(f => {
      const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      group.setAttribute('class', 'marker-pin' + (state.selectedFacility && state.selectedFacility.id === f.id ? ' active' : ''));
      group.setAttribute('data-id', f.id);
      group.setAttribute('transform', `translate(${f.x}, ${f.y})`);

      const color = getCategoryColor(f.category);

      // Pin background aura for selected
      if (state.selectedFacility && state.selectedFacility.id === f.id) {
        const aura = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        aura.setAttribute('class', 'marker-pulse');
        aura.setAttribute('cx', 0);
        aura.setAttribute('cy', 0);
        aura.setAttribute('fill', color);
        group.appendChild(aura);
      }

      // Pin marker circle
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', 0);
      circle.setAttribute('cy', 0);
      circle.setAttribute('r', 8);
      circle.setAttribute('fill', color);
      circle.setAttribute('stroke', '#ffffff');
      circle.setAttribute('stroke-width', '1.5');
      group.appendChild(circle);

      // Marker inner dot
      const innerDot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      innerDot.setAttribute('cx', 0);
      innerDot.setAttribute('cy', 0);
      innerDot.setAttribute('r', 3);
      innerDot.setAttribute('fill', '#05070a');
      group.appendChild(innerDot);

      // Click event
      group.addEventListener('click', (e) => {
        e.stopPropagation();
        selectFacility(f.id, true);
      });

      // Hover Tooltip
      group.addEventListener('mouseenter', (e) => {
        showMapTooltip(f, e);
      });
      group.addEventListener('mouseleave', () => {
        hideMapTooltip();
      });

      els.mapMarkersLayer.appendChild(group);
    });
  }

  function showMapTooltip(facility, evt) {
    els.mapTooltipLayer.innerHTML = `
      <g transform="translate(${facility.x}, ${facility.y - 18})">
        <rect x="-70" y="-32" width="140" height="28" rx="4" fill="rgba(10,14,18,0.92)" stroke="var(--line-strong)" stroke-width="1"/>
        <text x="0" y="-14" fill="#dfe7e0" font-family="Onest, sans-serif" font-size="9" font-weight="600" text-anchor="middle">
          ${escapeHTML(facility.name.length > 20 ? facility.name.substring(0, 18) + '...' : facility.name)}
        </text>
      </g>
    `;
  }

  function hideMapTooltip() {
    els.mapTooltipLayer.innerHTML = '';
  }

  // -------------------------------------------------------------
  // Select Facility & Show Details
  // -------------------------------------------------------------
  function selectFacility(id, shouldCenter = false) {
    const f = state.facilities.find(item => item.id === id);
    if (!f) return;

    state.selectedFacility = f;
    addToRecentlyViewed(f);

    // Update list selection highlight
    document.querySelectorAll('.facility-card-item').forEach(el => {
      el.classList.toggle('selected', parseInt(el.getAttribute('data-id'), 10) === id);
    });

    // Re-render markers to update active pulse
    renderMarkers(getCurrentFilteredFacilities());

    // Center map on marker
    if (shouldCenter && window.panMapTo) {
      window.panMapTo(f.x, f.y);
    }

    // Populate Details Card
    const color = getCategoryColor(f.category);
    els.detailCategoryBadge.textContent = f.category;
    els.detailCategoryBadge.style.borderColor = color;
    els.detailCategoryBadge.style.color = color;

    els.detailName.textContent = f.name;
    els.detailBuilding.textContent = f.building;
    els.detailFloor.textContent = f.floor;
    els.detailHours.textContent = f.operating_hours;

    if (f.contact) {
      els.detailContact.textContent = f.contact;
      els.detailContactRow.style.display = 'flex';
    } else {
      els.detailContactRow.style.display = 'none';
    }

    els.detailDesc.textContent = f.description;

    const statusDot = els.detailLiveStatus.querySelector('.status-indicator-dot');
    statusDot.className = 'status-indicator-dot ' + (f.is_open ? 'status-open' : 'status-closed');
    els.detailStatusText.textContent = f.status_badge || (f.is_open ? 'Open now' : 'Closed');
    els.detailStatusText.style.color = f.is_open ? '#2ecc71' : '#e74c3c';

    els.detailCard.classList.add('active');

    // Wire Directions buttons
    els.btnDirectionsTo.onclick = () => {
      openRouteDrawer();
      els.routeToSelect.value = f.id;
      state.route.toId = f.id;
      if (state.route.fromId && state.route.fromId !== state.route.toId) {
        calculateRoute();
      } else {
        showToast(`Set destination to ${f.name}. Choose an origin.`);
      }
    };

    els.btnDirectionsFrom.onclick = () => {
      openRouteDrawer();
      els.routeFromSelect.value = f.id;
      state.route.fromId = f.id;
      if (state.route.toId && state.route.fromId !== state.route.toId) {
        calculateRoute();
      } else {
        showToast(`Set origin to ${f.name}. Choose a destination.`);
      }
    };
  }

  function getCurrentFilteredFacilities() {
    const q = state.searchQuery.trim().toLowerCase();
    const cat = state.categoryFilter.toLowerCase();
    const bld = state.buildingFilter.toLowerCase();
    return state.facilities.filter(f => {
      const matchesQ = !q || (
        f.name.toLowerCase().includes(q) ||
        f.building.toLowerCase().includes(q) ||
        f.floor.toLowerCase().includes(q) ||
        f.description.toLowerCase().includes(q) ||
        f.category.toLowerCase().includes(q)
      );
      const matchesCat = cat === 'all' || f.category.toLowerCase() === cat;
      const matchesBld = bld === 'all' || f.building.toLowerCase() === bld;
      return matchesQ && matchesCat && matchesBld;
    });
  }

  // -------------------------------------------------------------
  // Route Guidance (Dijkstra)
  // -------------------------------------------------------------
  function openRouteDrawer() {
    els.routeDrawer.classList.add('active');
  }

  function closeRouteDrawer() {
    els.routeDrawer.classList.remove('active');
    clearRouteDisplay();
  }

  function clearRouteDisplay() {
    els.mapRouteLayer.innerHTML = '';
    els.routeSummaryCard.style.display = 'none';
    els.routeStepsContainer.innerHTML = '<div style="font-size: 11px; color: var(--muted); text-align: center; padding: 12px;">Select an origin and destination to compute the shortest walking route.</div>';
  }

  async function calculateRoute() {
    const fromId = parseInt(els.routeFromSelect.value, 10);
    const toId = parseInt(els.routeToSelect.value, 10);

    if (!fromId || !toId) {
      clearRouteDisplay();
      return;
    }

    try {
      const res = await fetch(`/api/route?from=${fromId}&to=${toId}`).then(r => r.json());
      if (!res.success) {
        showToast(res.error || 'No route found');
        els.routeSummaryCard.style.display = 'none';
        els.routeStepsContainer.innerHTML = `<div style="font-size: 12px; color: var(--ember); text-align: center; padding: 12px;">${escapeHTML(res.error || 'No route found.')}</div>`;
        els.mapRouteLayer.innerHTML = '';
        return;
      }

      state.route.data = res;
      renderRouteOnMap(res);
      renderRouteSteps(res);
      showToast(`Route found: ${res.total_distance} m (${res.walking_time_formatted})`);
    } catch (err) {
      console.error('Route calculation error:', err);
      showToast('Error calculating route');
    }
  }

  function renderRouteOnMap(routeData) {
    els.mapRouteLayer.innerHTML = '';
    const coords = routeData.coordinates;
    if (!coords || coords.length < 2) return;

    // Build polyline points string
    const pointsStr = coords.map(pt => `${pt[0]},${pt[1]}`).join(' ');

    // Polyline glow background
    const bgLine = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    bgLine.setAttribute('points', pointsStr);
    bgLine.setAttribute('fill', 'none');
    bgLine.setAttribute('stroke', 'rgba(224, 35, 28, 0.3)');
    bgLine.setAttribute('stroke-width', '10');
    bgLine.setAttribute('stroke-linecap', 'round');
    bgLine.setAttribute('stroke-linejoin', 'round');
    els.mapRouteLayer.appendChild(bgLine);

    // Polyline dashed active line
    const activeLine = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    activeLine.setAttribute('class', 'route-polyline');
    activeLine.setAttribute('points', pointsStr);
    els.mapRouteLayer.appendChild(activeLine);

    // Origin marker circle
    const startPt = coords[0];
    const startCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    startCircle.setAttribute('cx', startPt[0]);
    startCircle.setAttribute('cy', startPt[1]);
    startCircle.setAttribute('r', 7);
    startCircle.setAttribute('fill', '#e0231c');
    startCircle.setAttribute('stroke', '#ffffff');
    startCircle.setAttribute('stroke-width', '2');
    els.mapRouteLayer.appendChild(startCircle);

    // Destination marker circle
    const endPt = coords[coords.length - 1];
    const endCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    endCircle.setAttribute('cx', endPt[0]);
    endCircle.setAttribute('cy', endPt[1]);
    endCircle.setAttribute('r', 7);
    endCircle.setAttribute('fill', '#c9a24a');
    endCircle.setAttribute('stroke', '#ffffff');
    endCircle.setAttribute('stroke-width', '2');
    els.mapRouteLayer.appendChild(endCircle);
  }

  function renderRouteSteps(routeData) {
    els.routeDistVal.textContent = `${routeData.total_distance} m`;
    els.routeTimeVal.textContent = routeData.walking_time_formatted;
    els.routeSummaryCard.style.display = 'flex';

    els.routeStepsContainer.innerHTML = '';
    routeData.steps.forEach((step, idx) => {
      const stepItem = document.createElement('div');
      stepItem.className = 'route-step-item';
      stepItem.innerHTML = `
        <span class="step-num">${idx + 1}.</span>
        <span>${escapeHTML(step)}</span>
      `;
      els.routeStepsContainer.appendChild(stepItem);
    });
  }

  // -------------------------------------------------------------
  // Recently Viewed & LocalStorage
  // -------------------------------------------------------------
  function loadRecentlyViewed() {
    try {
      const raw = localStorage.getItem('sspu_recent_facilities');
      if (raw) state.recentlyViewed = JSON.parse(raw);
    } catch (e) {
      state.recentlyViewed = [];
    }
  }

  function addToRecentlyViewed(facility) {
    state.recentlyViewed = state.recentlyViewed.filter(id => id !== facility.id);
    state.recentlyViewed.unshift(facility.id);
    if (state.recentlyViewed.length > 5) state.recentlyViewed.pop();
    try {
      localStorage.setItem('sspu_recent_facilities', JSON.stringify(state.recentlyViewed));
    } catch (e) {}
    updateRecentPillsUI();
  }

  function updateRecentPillsUI() {
    if (!els.recentPills) return;
    if (state.recentlyViewed.length === 0) {
      els.recentPills.innerHTML = '<span style="color: var(--muted); font-size: 10px;">No recent places</span>';
      return;
    }
    els.recentPills.innerHTML = '';
    state.recentlyViewed.forEach(id => {
      const f = state.facilities.find(item => item.id === id);
      if (f) {
        const pill = document.createElement('button');
        pill.type = 'button';
        pill.className = 'quick-pill';
        pill.textContent = f.name.length > 18 ? f.name.substring(0, 16) + '...' : f.name;
        pill.addEventListener('click', () => selectFacility(f.id, true));
        els.recentPills.appendChild(pill);
      }
    });
  }

  // -------------------------------------------------------------
  // Ask Campus Assistant (Natural Language Query)
  // -------------------------------------------------------------
  function setupAskCampus() {
    els.openAskBtn.addEventListener('click', () => {
      els.askModal.classList.add('active');
      els.askInput.focus();
    });

    els.closeAskBtn.addEventListener('click', () => {
      els.askModal.classList.remove('active');
    });

    els.askModal.addEventListener('click', (e) => {
      if (e.target === els.askModal) els.askModal.classList.remove('active');
    });

    els.askForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const question = els.askInput.value.trim();
      if (!question) return;

      els.askAnswerBox.style.display = 'block';
      els.askAnswerText.textContent = 'Searching campus knowledge base...';
      els.askMatchedPills.innerHTML = '';

      try {
        const res = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question })
        }).then(r => r.json());

        if (res.success) {
          els.askAnswerText.textContent = res.answer;
          if (res.matched_facility_ids && res.matched_facility_ids.length > 0) {
            res.matched_facility_ids.forEach(id => {
              const f = state.facilities.find(item => item.id === id);
              if (f) {
                const pill = document.createElement('button');
                pill.type = 'button';
                pill.className = 'quick-pill';
                pill.style.borderColor = 'var(--vermilion)';
                pill.textContent = `📍 ${f.name}`;
                pill.addEventListener('click', () => {
                  els.askModal.classList.remove('active');
                  selectFacility(f.id, true);
                });
                els.askMatchedPills.appendChild(pill);
              }
            });
          }
        } else {
          els.askAnswerText.textContent = res.error || 'Could not find relevant facilities.';
        }
      } catch (err) {
        els.askAnswerText.textContent = 'Error contacting campus assistant.';
      }
    });
  }

  // -------------------------------------------------------------
  // Event Listeners
  // -------------------------------------------------------------
  function setupEventListeners() {
    // Search input
    let searchDebounce;
    els.searchInput.addEventListener('input', (e) => {
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => {
        state.searchQuery = e.target.value;
        applyFilters();
      }, 150);
    });

    els.searchClearBtn.addEventListener('click', () => {
      els.searchInput.value = '';
      state.searchQuery = '';
      applyFilters();
      els.searchInput.focus();
    });

    // Building filter
    els.buildingSelect.addEventListener('change', (e) => {
      state.buildingFilter = e.target.value;
      applyFilters();
    });

    // Reset filters
    els.resetFiltersBtn.addEventListener('click', () => {
      state.searchQuery = '';
      state.categoryFilter = 'all';
      state.buildingFilter = 'all';
      els.searchInput.value = '';
      els.buildingSelect.value = 'all';
      populateCategoryChips();
      applyFilters();
      showToast('Filters cleared');
    });

    // Details close
    els.detailCloseBtn.addEventListener('click', () => {
      els.detailCard.classList.remove('active');
      state.selectedFacility = null;
      renderMarkers(getCurrentFilteredFacilities());
      document.querySelectorAll('.facility-card-item').forEach(el => el.classList.remove('selected'));
    });

    // Route drawer events
    els.navRouteToggle.addEventListener('click', () => {
      if (els.routeDrawer.classList.contains('active')) {
        closeRouteDrawer();
      } else {
        openRouteDrawer();
      }
    });

    els.routeCloseBtn.addEventListener('click', closeRouteDrawer);

    els.routeFromSelect.addEventListener('change', () => {
      state.route.fromId = parseInt(els.routeFromSelect.value, 10);
      calculateRoute();
    });

    els.routeToSelect.addEventListener('change', () => {
      state.route.toId = parseInt(els.routeToSelect.value, 10);
      calculateRoute();
    });

    // Building clicks on SVG
    document.querySelectorAll('.building-block').forEach(b => {
      b.addEventListener('click', () => {
        const bldName = b.getAttribute('data-building');
        if (bldName) {
          state.buildingFilter = bldName;
          els.buildingSelect.value = bldName;
          applyFilters();
          showToast(`Filtered by ${bldName}`);
        }
      });
    });

    setupAskCampus();
  }

  // -------------------------------------------------------------
  // Utilities
  // -------------------------------------------------------------
  function showToast(msg) {
    if (!els.toastContainer) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    els.toastContainer.appendChild(toast);
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

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
