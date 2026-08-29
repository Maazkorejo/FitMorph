// FitMorph Mobile Application Engine
const API_BASE = '/api';

// Application State
let currentUser = null;
let currentToken = localStorage.getItem('fitmorph_token') || null;
let activePlan = null;
let activeDayIndex = 0;
let currentPage = 'page-home';

// API Helper
async function apiRequest(endpoint, options = {}) {
  const headers = { ...options.headers };
  if (currentToken) {
    headers['Authorization'] = `Bearer ${currentToken}`;
  }
  
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });
    
    if (response.status === 401) {
      handleLogout();
      showToast('Session expired. Please log in.', 'warning');
      return null;
    }
    
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const errorMsg = data?.detail || 'An unexpected error occurred';
      throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    }
    return data;
  } catch (err) {
    showToast(err.message, 'danger');
    throw err;
  }
}

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = '⚡';
  if (type === 'success') icon = '✅';
  if (type === 'danger') icon = '⚠️';
  if (type === 'warning') icon = '🛡️';
  
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

// Side Drawer Navigation (Opens upon pressing hamburger)
function toggleDrawer(open = null) {
  const overlay = document.getElementById('side-drawer-overlay');
  if (!overlay) return;
  
  if (open === true) {
    overlay.classList.add('open');
  } else if (open === false) {
    overlay.classList.remove('open');
  } else {
    overlay.classList.toggle('open');
  }
}

// Page Routing (Desktop and Mobile)
function navTo(pageId) {
  const pages = document.querySelectorAll('.app-page-view, .mobile-page');
  pages.forEach(p => p.classList.remove('active'));
  
  const target = document.getElementById(pageId);
  if (target) {
    target.classList.add('active');
    currentPage = pageId;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  // Update desktop navigation active states
  document.querySelectorAll('.desktop-nav-link').forEach(link => {
    if (link.getAttribute('data-target') === pageId) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Update bottom navigation active states
  document.querySelectorAll('.bottom-nav-tab').forEach(tab => {
    if (tab.getAttribute('data-target') === pageId) {
      tab.classList.add('active');
    } else {
      tab.classList.remove('active');
    }
  });
  
  // Update side drawer link states
  document.querySelectorAll('.drawer-menu-link').forEach(link => {
    if (link.getAttribute('data-target') === pageId) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
  
  // Close the side drawer upon navigation
  toggleDrawer(false);
}

// Authentication & Session
async function checkAuth() {
  if (!currentToken) {
    showAuthModal(true);
    return;
  }
  try {
    currentUser = await apiRequest('/auth/me');
    if (currentUser) {
      updateUserUI();
      loadProfile();
      loadActiveWorkout();
      loadVolumeSummary();
      loadPlateauStatus();
      loadCoachAdvice();
    }
  } catch (e) {
    handleLogout();
  }
}

function updateUserUI() {
  showAuthModal(false);
  const displayName = currentUser?.full_name || currentUser?.email?.split('@')[0] || 'Athlete';
  const email = currentUser?.email || 'athlete@fitmorph.com';
  
  const topAvatar = document.getElementById('top-bar-avatar');
  if (topAvatar) topAvatar.textContent = displayName.charAt(0).toUpperCase();

  const topName = document.getElementById('top-bar-name');
  if (topName) topName.textContent = displayName;

  const homeGreeting = document.getElementById('home-greeting-name');
  if (homeGreeting) homeGreeting.textContent = displayName;
  
  const drawerName = document.getElementById('drawer-athlete-name');
  if (drawerName) drawerName.textContent = displayName;
  
  const drawerEmail = document.getElementById('drawer-athlete-email');
  if (drawerEmail) drawerEmail.textContent = email;
  
  const drawerAvatar = document.getElementById('drawer-athlete-avatar');
  if (drawerAvatar) drawerAvatar.textContent = displayName.charAt(0).toUpperCase();
}

function handleLogout() {
  currentToken = null;
  currentUser = null;
  localStorage.removeItem('fitmorph_token');
  showAuthModal(true);
  toggleDrawer(false);
}

function showAuthModal(show = true) {
  const modal = document.getElementById('auth-modal');
  if (modal) {
    if (show) modal.classList.add('open');
    else modal.classList.remove('open');
  }
}

// Profile & Biometrics Hub
async function loadProfile() {
  try {
    const profile = await apiRequest('/profile');
    if (profile) {
      document.getElementById('prof-gender').value = profile.gender;
      document.getElementById('prof-age').value = profile.age;
      document.getElementById('prof-height').value = profile.height_cm;
      document.getElementById('prof-weight').value = profile.weight_kg;
      document.getElementById('prof-goal').value = profile.fitness_goal;
      document.getElementById('prof-equip').value = profile.equipment_access;
      
      updateBMIDisplay(profile.bmi, profile.bmi_category);
      
      const homeBmi = document.getElementById('home-stat-bmi');
      if (homeBmi) homeBmi.textContent = profile.bmi.toFixed(1);
      
      const homeGoal = document.getElementById('home-stat-goal');
      if (homeGoal) homeGoal.textContent = profile.fitness_goal.replace('_', ' ').toUpperCase();
      
      const injuries = profile.injury_list || [];
      document.querySelectorAll('.shield-chip-btn').forEach(chip => {
        const val = chip.getAttribute('data-injury');
        if (injuries.includes(val)) {
          chip.classList.add('active');
        } else {
          chip.classList.remove('active');
        }
      });
      
      const homeShield = document.getElementById('home-stat-shield');
      if (homeShield) {
        homeShield.textContent = injuries.length > 0 ? `${injuries.length} Shield(s)` : 'Full Range';
      }
    }
  } catch (e) {}
}

function updateBMIDisplay(bmi, category) {
  const bmiVal = document.getElementById('bmi-number');
  const bmiPill = document.getElementById('bmi-status-pill');
  if (bmiVal) bmiVal.textContent = bmi.toFixed(1);
  if (bmiPill) {
    bmiPill.textContent = category.toUpperCase();
    bmiPill.className = 'metric-pill';
    if (category === 'normal') bmiPill.classList.add('pill-mint');
    else if (category === 'overweight') bmiPill.classList.add('pill-amber');
    else if (category === 'obese') bmiPill.classList.add('pill-crimson');
    else bmiPill.classList.add('pill-cyan');
  }
}

async function handleProfileSave(e) {
  e.preventDefault();
  const gender = document.getElementById('prof-gender').value;
  const age = parseInt(document.getElementById('prof-age').value);
  const height = parseFloat(document.getElementById('prof-height').value);
  const weight = parseFloat(document.getElementById('prof-weight').value);
  const goal = document.getElementById('prof-goal').value;
  const equip = document.getElementById('prof-equip').value;
  
  const activeChips = Array.from(document.querySelectorAll('.shield-chip-btn.active')).map(c => c.getAttribute('data-injury'));
  const injuries = activeChips.length > 0 ? activeChips.join(',') : 'none';
  
  try {
    const profile = await apiRequest('/profile', {
      method: 'POST',
      body: JSON.stringify({
        gender,
        age,
        height_cm: height,
        weight_kg: weight,
        fitness_goal: goal,
        equipment_access: equip,
        injuries
      })
    });
    showToast('Biometrics & Injury Shield updated!', 'success');
    updateBMIDisplay(profile.bmi, profile.bmi_category);
    loadProfile();
  } catch (e) {}
}

// Workout Generation & Blueprint
async function handleGenerateWorkout() {
  const btn = document.getElementById('btn-recalibrate-workout');
  if (btn) btn.disabled = true;
  showToast('Synthesizing 4-week periodized split...', 'info');
  
  try {
    const plan = await apiRequest('/workouts/generate', {
      method: 'POST',
      body: JSON.stringify({})
    });
    activePlan = plan;
    renderWorkoutPlan(plan);
    showToast('Workout Blueprint generated!', 'success');
  } catch (e) {
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function loadActiveWorkout() {
  try {
    const plan = await apiRequest('/workouts/active');
    activePlan = plan;
    renderWorkoutPlan(plan);
    
    const homePlan = document.getElementById('home-featured-title');
    if (homePlan) homePlan.textContent = plan.title;
  } catch (e) {
    const container = document.getElementById('workout-mobile-list');
    if (container) {
      container.innerHTML = `
        <div style="text-align: center; padding: 30px 10px;">
          <p style="color: var(--text-sub); margin-bottom: 15px; font-size: 0.9rem;">No active routine generated.</p>
          <button class="mobile-btn btn-neon-mint" onclick="handleGenerateWorkout()">⚡ Generate 4-Week Routine</button>
        </div>
      `;
    }
  }
}

function renderWorkoutPlan(plan) {
  const container = document.getElementById('workout-mobile-list');
  if (!container) return;
  
  let daysNav = '<div style="display: flex; gap: 8px; margin-bottom: 14px; overflow-x: auto; padding-bottom: 4px;">';
  plan.days.forEach((day, idx) => {
    const activeCls = idx === activeDayIndex ? 'btn-neon-mint' : 'btn-dark-sub';
    daysNav += `<button class="mobile-btn btn-mini ${activeCls}" onclick="selectWorkoutDay(${idx})">Day ${day.day_number}</button>`;
  });
  daysNav += '</div>';
  
  const currentDay = plan.days[activeDayIndex] || plan.days[0];
  
  let exercisesHtml = '';
  currentDay.exercises.forEach(ex => {
    const swapTag = ex.is_swap ? '<span class="metric-pill pill-cyan" style="font-size: 0.65rem; padding: 2px 6px;">SWAPPED</span>' : '';
    exercisesHtml += `
      <div class="exercise-mobile-item">
        <div class="exercise-info-block">
          <div class="exercise-title-text">${ex.name} ${swapTag}</div>
          <div class="exercise-tags-line">
            <span>${ex.sets} Sets &times; ${ex.reps} Reps</span>
            <span>⏱️ ${ex.rest_seconds}s Rest</span>
            <span>RPE ${ex.rpe_target}</span>
          </div>
          <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px;">💡 ${ex.cues}</div>
        </div>
        <div>
          <button class="mobile-btn btn-mini btn-dark-sub" onclick="promptExerciseSwap(${currentDay.id}, '${ex.name.replace(/'/g, "\\'")}')">🔄 Swap</button>
        </div>
      </div>
    `;
  });
  
  container.innerHTML = `
    <div style="margin-bottom: 12px;">
      <h3 style="font-size: 1.15rem; font-weight: 800;">${plan.title}</h3>
      <div style="font-size: 0.78rem; color: var(--text-sub); margin-top: 2px;">Split: <b>${plan.split_type}</b> &bull; Equipment: <b>${plan.equipment.replace('_', ' ').toUpperCase()}</b></div>
    </div>
    ${daysNav}
    <div class="app-card" style="padding: 12px; margin-bottom: 12px; background: var(--card-bg-elevated);">
      <span class="metric-pill pill-cyan" style="font-size: 0.7rem; margin-bottom: 4px;">Cardio & Conditioning</span>
      <div style="font-size: 0.85rem; color: var(--text-main); font-weight: 600;">${currentDay.cardio_protocol}</div>
    </div>
    <div>${exercisesHtml}</div>
  `;
}

function selectWorkoutDay(idx) {
  activeDayIndex = idx;
  if (activePlan) renderWorkoutPlan(activePlan);
}

// 1-Click Joint Safe Swap
async function promptExerciseSwap(dayId, exerciseName) {
  showToast(`Finding safe replacement for "${exerciseName}"...`, 'info');
  try {
    const swapResult = await apiRequest('/workouts/swap', {
      method: 'POST',
      body: JSON.stringify({
        day_id: dayId,
        exercise_name: exerciseName,
        reason: 'joint_discomfort'
      })
    });
    showToast(`Substituted with: ${swapResult.replacement.name}!`, 'success');
    loadActiveWorkout();
  } catch (e) {}
}

// Force & Set Logging
async function handleSetLog(e) {
  e.preventDefault();
  const name = document.getElementById('log-ex-name').value;
  const muscle = document.getElementById('log-muscle').value;
  const sets = parseInt(document.getElementById('log-set-num').value);
  const weight = parseFloat(document.getElementById('log-weight').value);
  const reps = parseInt(document.getElementById('log-reps').value);
  const rpe = parseFloat(document.getElementById('log-rpe').value);
  
  try {
    const logged = await apiRequest('/logs/set', {
      method: 'POST',
      body: JSON.stringify({
        exercise_name: name,
        muscle_group: muscle,
        set_number: sets,
        weight_kg: weight,
        reps,
        rpe
      })
    });
    showToast(`Logged! Tonnage: ${logged.volume_load}kg | 1RM: ${logged.estimated_one_rep_max}kg`, 'success');
    loadVolumeSummary();
    loadPlateauStatus();
  } catch (e) {}
}

// Volume & Deload Monitoring
async function loadVolumeSummary() {
  try {
    const summary = await apiRequest('/logs/summary');
    if (summary) {
      const volTxt = `${summary.total_volume_kg.toLocaleString()} kg`;
      const setsTxt = summary.total_sets;
      
      const homeVol = document.getElementById('home-stat-volume');
      if (homeVol) homeVol.textContent = volTxt;
      
      const hubVol = document.getElementById('hub-stat-volume');
      if (hubVol) hubVol.textContent = volTxt;
      
      const hubSets = document.getElementById('hub-stat-sets');
      if (hubSets) hubSets.textContent = setsTxt;
      
      const hubChange = document.getElementById('hub-stat-change');
      if (hubChange) {
        hubChange.textContent = `${summary.weekly_change_pct > 0 ? '+' : ''}${summary.weekly_change_pct}% vs prior week`;
        hubChange.style.color = summary.weekly_change_pct >= 0 ? 'var(--neon-mint)' : 'var(--danger)';
      }
    }
  } catch (e) {}
}

async function loadPlateauStatus() {
  try {
    const status = await apiRequest('/plateau/status');
    const badge = document.getElementById('hub-plateau-badge');
    const recText = document.getElementById('hub-plateau-rec');
    
    if (badge) {
      if (status.deload_scheduled || status.plateau_detected) {
        badge.textContent = 'DELOAD SCHEDULED';
        badge.className = 'metric-pill pill-amber';
      } else {
        badge.textContent = 'PROGRESSIVE OVERLOAD';
        badge.className = 'metric-pill pill-mint';
      }
    }
    if (recText) recText.textContent = status.coaching_recommendation;
  } catch (e) {}
}

async function triggerManualDeloadAudit() {
  showToast('Auditing 14-day progressive overload...', 'info');
  try {
    const res = await apiRequest('/plateau/trigger-audit', { method: 'POST' });
    showToast(res.message, 'success');
    loadPlateauStatus();
  } catch (e) {}
}

// AI Vision Physique Scanner
async function handlePhysiqueUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('scan-file-input');
  const monthInput = document.getElementById('scan-month-select');
  
  if (!fileInput.files || fileInput.files.length === 0) {
    showToast('Please choose a physique photo', 'warning');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('month_number', monthInput.value || 1);
  
  const scanBtn = document.getElementById('btn-submit-scan');
  scanBtn.disabled = true;
  scanBtn.textContent = 'Analyzing Symmetry...';
  showToast('Gemini Flash Vision evaluating posture and symmetry...', 'info');
  
  try {
    const scan = await apiRequest('/physique/scan', {
      method: 'POST',
      body: formData
    });
    renderPhysiqueScanResult(scan);
    showToast('Symmetry assessment complete!', 'success');
  } catch (e) {
  } finally {
    scanBtn.disabled = false;
    scanBtn.textContent = '🔍 Analyze Check-In Photo';
  }
}

function renderPhysiqueScanResult(scan) {
  const resultCard = document.getElementById('scan-result-card');
  if (!resultCard) return;
  
  resultCard.style.display = 'block';
  document.getElementById('res-scan-score').textContent = `${scan.symmetry_score.toFixed(1)} / 100`;
  document.getElementById('res-scan-posture').textContent = scan.posture_assessment;
  document.getElementById('res-scan-strong').textContent = scan.strong_muscle_groups;
  document.getElementById('res-scan-lagging').textContent = scan.lagging_muscle_groups;
  document.getElementById('res-scan-notes').textContent = scan.ai_analysis_notes;
  
  const bonusBox = document.getElementById('res-scan-bonus');
  if (bonusBox && scan.bonus_exercises) {
    bonusBox.innerHTML = scan.bonus_exercises.map(b => `
      <div style="background: var(--card-bg-elevated); border: 1px solid var(--card-border); border-radius: 12px; padding: 10px; margin-top: 6px;">
        <div style="font-weight: 700; font-size: 0.88rem;">${b.name} (${b.target_muscle})</div>
        <div style="font-size: 0.78rem; color: var(--neon-mint);">${b.sets} Sets &times; ${b.reps} Reps</div>
        <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 2px;">${b.reason}</div>
      </div>
    `).join('');
  }
}

// AI Coach Advice
async function loadCoachAdvice() {
  try {
    const res = await apiRequest('/coach/advice');
    const adviceEl = document.getElementById('coach-advice-box');
    if (adviceEl && res) {
      adviceEl.innerHTML = res.advice.replace(/\n/g, '<br>');
    }
  } catch (e) {}
}

// Executive PDF Dossier Download
async function downloadPdfReport() {
  if (!currentToken) {
    showToast('Please log in first', 'warning');
    showAuthModal(true);
    return;
  }
  showToast('Generating personalized 4-week PDF dossier via ReportLab...', 'info');
  try {
    const response = await fetch(`/api/reports/download?token=${encodeURIComponent(currentToken)}`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Failed to generate PDF' }));
      throw new Error(err.detail || 'Download failed');
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fitmorph_blueprint_${Date.now()}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
    showToast('PDF Blueprint downloaded successfully!', 'success');
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// Initialization on DOM Load
document.addEventListener('DOMContentLoaded', () => {
  // Drawer Toggle Handlers
  const menuBtn = document.getElementById('btn-open-drawer');
  if (menuBtn) menuBtn.addEventListener('click', () => toggleDrawer(true));
  
  const closeBtn = document.getElementById('btn-close-drawer');
  if (closeBtn) closeBtn.addEventListener('click', () => toggleDrawer(false));
  
  const drawerOverlay = document.getElementById('side-drawer-overlay');
  if (drawerOverlay) {
    drawerOverlay.addEventListener('click', (e) => {
      if (e.target === drawerOverlay) toggleDrawer(false);
    });
  }
  
  // Bottom Nav & Drawer Click Handlers
  document.querySelectorAll('[data-target]').forEach(elem => {
    elem.addEventListener('click', (e) => {
      e.preventDefault();
      const target = elem.getAttribute('data-target');
      if (target) navTo(target);
    });
  });
  
  // Injury Chip Toggles
  document.querySelectorAll('.shield-chip-btn').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('active');
    });
  });
  
  // Forms
  const profForm = document.getElementById('mobile-profile-form');
  if (profForm) profForm.addEventListener('submit', handleProfileSave);
  
  const logForm = document.getElementById('mobile-log-form');
  if (logForm) logForm.addEventListener('submit', handleSetLog);
  
  const scanForm = document.getElementById('mobile-scan-form');
  if (scanForm) scanForm.addEventListener('submit', handlePhysiqueUpload);
  
  const fileInput = document.getElementById('scan-file-input');
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const preview = document.getElementById('scan-preview-img');
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
      }
    });
  }
  
  // Auth Form
  const authForm = document.getElementById('mobile-auth-form');
  if (authForm) {
    authForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('auth-email').value;
      const password = document.getElementById('auth-password').value;
      const isSignup = document.getElementById('auth-is-signup').checked;
      
      try {
        if (isSignup) {
          await apiRequest('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ email, password })
          });
          showToast('Account created! Authenticating...', 'success');
        }
        
        const tokenData = await apiRequest('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password })
        });
        
        currentToken = tokenData.access_token;
        localStorage.setItem('fitmorph_token', currentToken);
        showToast('Logged in successfully!', 'success');
        checkAuth();
      } catch (err) {}
    });
  }
  
  checkAuth();
});
