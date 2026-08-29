// FitMorph Athletic Intelligence - Client Application Engine
const API_BASE = '/api';

// Application State
let currentUser = null;
let currentToken = localStorage.getItem('fitmorph_token') || null;
let activePlan = null;
let activeDayIndex = 0;
let currentPageView = 'view-dashboard';

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
      showToast('Session authorization expired. Please log in.', 'warning');
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
  }, 4000);
}

// Side Navigation Drawer Toggle
function toggleSidebar(open = null) {
  const overlay = document.getElementById('sidebar-overlay');
  if (!overlay) return;
  
  if (open === true) {
    overlay.classList.add('active');
  } else if (open === false) {
    overlay.classList.remove('active');
  } else {
    overlay.classList.toggle('active');
  }
}

// Page View Navigation Router
function navigateTo(pageId) {
  const pages = document.querySelectorAll('.page-view');
  pages.forEach(p => p.classList.remove('active'));
  
  const targetPage = document.getElementById(pageId);
  if (targetPage) {
    targetPage.classList.add('active');
    currentPageView = pageId;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  // Update active sidebar nav item
  const navLinks = document.querySelectorAll('.sidebar-nav-link');
  navLinks.forEach(link => {
    if (link.getAttribute('data-target') === pageId) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
  
  // Close the drawer upon navigating
  toggleSidebar(false);
}

// Authentication Check
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
  const authModal = document.getElementById('auth-modal');
  if (authModal) authModal.classList.remove('open');
  
  const navUserEl = document.getElementById('nav-user-email');
  const sideUserEl = document.getElementById('sidebar-user-name');
  const sideEmailEl = document.getElementById('sidebar-user-email');
  const sideAvatarEl = document.getElementById('sidebar-user-avatar');
  
  const displayName = currentUser?.full_name || currentUser?.email?.split('@')[0] || 'Athlete';
  
  if (navUserEl) navUserEl.textContent = displayName;
  if (sideUserEl) sideUserEl.textContent = displayName;
  if (sideEmailEl) sideEmailEl.textContent = currentUser?.email || '';
  if (sideAvatarEl) sideAvatarEl.textContent = displayName.charAt(0).toUpperCase();
}

function handleLogout() {
  currentToken = null;
  currentUser = null;
  localStorage.removeItem('fitmorph_token');
  showAuthModal(true);
  toggleSidebar(false);
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
      
      // Update quick dash stats
      const dashBmi = document.getElementById('dash-stat-bmi');
      if (dashBmi) dashBmi.textContent = profile.bmi.toFixed(1);
      
      const dashGoal = document.getElementById('dash-stat-goal');
      if (dashGoal) dashGoal.textContent = profile.fitness_goal.replace('_', ' ').toUpperCase();
      
      // Update active injury chips
      const injuries = profile.injury_list || [];
      document.querySelectorAll('.injury-chip').forEach(chip => {
        const val = chip.getAttribute('data-injury');
        if (injuries.includes(val)) {
          chip.classList.add('active');
        } else {
          chip.classList.remove('active');
        }
      });
      
      const dashShield = document.getElementById('dash-stat-shield');
      if (dashShield) {
        if (injuries.length > 0) {
          dashShield.textContent = `${injuries.length} JOINT SHIELD(S) ACTIVE`;
          dashShield.className = 'badge badge-crimson';
        } else {
          dashShield.textContent = 'NO INJURIES (FULL RANGE)';
          dashShield.className = 'badge badge-emerald';
        }
      }
    }
  } catch (e) {}
}

function updateBMIDisplay(bmi, category) {
  const bmiValEl = document.getElementById('bmi-value');
  const bmiBadgeEl = document.getElementById('bmi-badge');
  if (bmiValEl) bmiValEl.textContent = bmi.toFixed(1);
  if (bmiBadgeEl) {
    bmiBadgeEl.textContent = category.toUpperCase();
    bmiBadgeEl.className = 'badge';
    if (category === 'normal') bmiBadgeEl.classList.add('badge-emerald');
    else if (category === 'overweight') bmiBadgeEl.classList.add('badge-amber');
    else if (category === 'obese') bmiBadgeEl.classList.add('badge-crimson');
    else bmiBadgeEl.classList.add('badge-cyan');
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
  
  const activeChips = Array.from(document.querySelectorAll('.injury-chip.active')).map(c => c.getAttribute('data-injury'));
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
    showToast('Biometric parameters and injury shield recalibrated!', 'success');
    updateBMIDisplay(profile.bmi, profile.bmi_category);
    loadCoachAdvice();
    loadProfile();
  } catch (e) {}
}

// Workout Generation & Blueprint
async function handleGenerateWorkout() {
  const btn = document.getElementById('btn-generate-workout');
  if (btn) btn.disabled = true;
  showToast('Synthesizing 4-week periodized split with injury shield constraints...', 'info');
  
  try {
    const plan = await apiRequest('/workouts/generate', {
      method: 'POST',
      body: JSON.stringify({})
    });
    activePlan = plan;
    renderWorkoutPlan(plan);
    showToast('Adaptive training blueprint generated successfully!', 'success');
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
    
    // Update dashboard split preview
    const dashPlanTitle = document.getElementById('dash-plan-title');
    if (dashPlanTitle) dashPlanTitle.textContent = plan.title;
  } catch (e) {
    const container = document.getElementById('workout-container');
    if (container) {
      container.innerHTML = `
        <div style="text-align: center; padding: 4rem 1.5rem;">
          <h3 style="font-size: 1.3rem; margin-bottom: 0.5rem;">No Active Training Blueprint Synthesized</h3>
          <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Generate an autoregulated periodization routine tailored to your body composition and equipment.</p>
          <button class="btn btn-primary" onclick="handleGenerateWorkout()">⚡ Synthesize 4-Week Blueprint</button>
        </div>
      `;
    }
  }
}

function renderWorkoutPlan(plan) {
  const container = document.getElementById('workout-container');
  if (!container) return;
  
  let daysNav = '<div style="display: flex; gap: 0.6rem; margin-bottom: 1.5rem; overflow-x: auto;">';
  plan.days.forEach((day, idx) => {
    const activeCls = idx === activeDayIndex ? 'btn-primary' : 'btn-secondary';
    daysNav += `<button class="btn ${activeCls} btn-sm" onclick="selectWorkoutDay(${idx})">Day ${day.day_number}: ${day.day_name.split(':')[1] || day.day_name}</button>`;
  });
  daysNav += '</div>';
  
  const currentDay = plan.days[activeDayIndex] || plan.days[0];
  
  let exercisesHtml = '';
  currentDay.exercises.forEach(ex => {
    const swapBadge = ex.is_swap ? '<span class="badge badge-cyan" style="margin-left: 0.5rem;">SUBSTITUTED</span>' : '';
    exercisesHtml += `
      <div class="exercise-item-card">
        <div class="exercise-meta">
          <div class="exercise-name">
            ${ex.name} ${swapBadge}
          </div>
          <div class="exercise-stats">
            <span><b>Target Volume:</b> ${ex.sets} Working Sets</span>
            <span><b>Intensity Bracket:</b> ${ex.reps} Reps</span>
            <span><b>Recovery Interval:</b> ${ex.rest_seconds}s</span>
            <span><b>Target RPE:</b> ${ex.rpe_target}</span>
          </div>
          <div class="exercise-cue">💡 <b>Biomechanical Cue:</b> ${ex.cues}</div>
        </div>
        <div>
          <button class="btn btn-secondary btn-sm" onclick="promptExerciseSwap(${currentDay.id}, '${ex.name.replace(/'/g, "\\'")}')">🔄 Safe Swap</button>
        </div>
      </div>
    `;
  });
  
  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
      <div>
        <h3 style="font-size: 1.35rem; font-weight: 800;">${plan.title}</h3>
        <p style="color: var(--text-secondary); font-size: 0.88rem;"><b>Split Architecture:</b> ${plan.split_type} &bull; <b>Equipment Tier:</b> ${plan.equipment.replace('_', ' ').toUpperCase()}</p>
      </div>
      <button class="btn btn-primary btn-sm" onclick="handleGenerateWorkout()">⚡ Recalibrate Routine</button>
    </div>
    ${daysNav}
    <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
      <span style="font-size: 0.8rem; font-weight: 800; color: var(--accent-cyan); text-transform: uppercase; letter-spacing: 1px;">Cardiovascular & Conditioning Protocol</span>
      <p style="color: var(--text-primary); font-size: 0.92rem; margin-top: 0.25rem;">${currentDay.cardio_protocol}</p>
    </div>
    <div class="exercise-list">
      ${exercisesHtml}
    </div>
  `;
}

function selectWorkoutDay(idx) {
  activeDayIndex = idx;
  if (activePlan) renderWorkoutPlan(activePlan);
}

// 1-Click Biomechanical Exercise Swap
async function promptExerciseSwap(dayId, exerciseName) {
  showToast(`Injury Shield searching for joint-safe equivalent for "${exerciseName}"...`, 'info');
  try {
    const swapResult = await apiRequest('/workouts/swap', {
      method: 'POST',
      body: JSON.stringify({
        day_id: dayId,
        exercise_name: exerciseName,
        reason: 'joint_discomfort'
      })
    });
    
    showToast(`Joint-safe substitute locked: ${swapResult.replacement.name}!`, 'success');
    loadActiveWorkout();
  } catch (e) {}
}

// Session Logging
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
    showToast(`Set logged! Tonnage: ${logged.volume_load}kg | Est. 1RM: ${logged.estimated_one_rep_max}kg`, 'success');
    loadVolumeSummary();
    loadPlateauStatus();
  } catch (e) {}
}

// Volume & Deload Monitoring
async function loadVolumeSummary() {
  try {
    const summary = await apiRequest('/logs/summary');
    if (summary) {
      document.getElementById('stat-total-volume').textContent = `${summary.total_volume_kg.toLocaleString()} kg`;
      document.getElementById('stat-total-sets').textContent = summary.total_sets;
      document.getElementById('stat-total-reps').textContent = summary.total_reps;
      
      const changeEl = document.getElementById('stat-volume-change');
      if (changeEl) {
        changeEl.textContent = `${summary.weekly_change_pct > 0 ? '+' : ''}${summary.weekly_change_pct}% vs prior 7 days`;
        changeEl.style.color = summary.weekly_change_pct >= 0 ? 'var(--accent-emerald)' : 'var(--danger)';
      }
      
      const dashVol = document.getElementById('dash-stat-volume');
      if (dashVol) dashVol.textContent = `${summary.total_volume_kg.toLocaleString()} kg`;
    }
  } catch (e) {}
}

async function loadPlateauStatus() {
  try {
    const status = await apiRequest('/plateau/status');
    const badge = document.getElementById('plateau-status-badge');
    const recText = document.getElementById('plateau-recommendation');
    
    if (badge) {
      if (status.deload_scheduled || status.plateau_detected) {
        badge.textContent = 'DELOAD WEEK SCHEDULED';
        badge.className = 'badge badge-amber';
      } else {
        badge.textContent = 'PROGRESSIVE OVERLOAD';
        badge.className = 'badge badge-emerald';
      }
    }
    if (recText) recText.textContent = status.coaching_recommendation;
  } catch (e) {}
}

async function triggerManualDeloadAudit() {
  showToast('APScheduler evaluating 14-day progressive overload trajectory...', 'info');
  try {
    const res = await apiRequest('/plateau/trigger-audit', { method: 'POST' });
    showToast(res.message, 'success');
    loadPlateauStatus();
  } catch (e) {}
}

// AI Vision Physique Scanner
async function handlePhysiqueUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('physique-file');
  const monthInput = document.getElementById('physique-month');
  
  if (!fileInput.files || fileInput.files.length === 0) {
    showToast('Please select a physique check-in image', 'warning');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('month_number', monthInput.value || 1);
  
  const scanBtn = document.getElementById('btn-scan-physique');
  scanBtn.disabled = true;
  scanBtn.textContent = 'Analyzing Symmetry & Posture...';
  showToast('Processing photo through Gemini Flash Vision & Biomechanical Model...', 'info');
  
  try {
    const scan = await apiRequest('/physique/scan', {
      method: 'POST',
      body: formData
    });
    
    renderPhysiqueScanResult(scan);
    showToast('Physique symmetry analysis completed!', 'success');
  } catch (e) {
  } finally {
    scanBtn.disabled = false;
    scanBtn.textContent = 'Upload & Analyze Physique';
  }
}

function renderPhysiqueScanResult(scan) {
  const resultContainer = document.getElementById('physique-result-card');
  if (!resultContainer) return;
  
  resultContainer.style.display = 'block';
  document.getElementById('scan-score').textContent = `${scan.symmetry_score.toFixed(1)} / 100`;
  document.getElementById('scan-posture').textContent = scan.posture_assessment;
  document.getElementById('scan-strong').textContent = scan.strong_muscle_groups;
  document.getElementById('scan-lagging').textContent = scan.lagging_muscle_groups;
  document.getElementById('scan-bodycomp').textContent = scan.estimated_body_composition;
  document.getElementById('scan-notes').textContent = scan.ai_analysis_notes;
  
  const bonusContainer = document.getElementById('scan-bonus-exercises');
  if (bonusContainer && scan.bonus_exercises) {
    bonusContainer.innerHTML = scan.bonus_exercises.map(b => `
      <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 0.75rem 1rem; margin-top: 0.5rem;">
        <b>${b.name}</b> (${b.target_muscle}): ${b.sets} Sets &times; ${b.reps} Reps
        <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">${b.reason}</div>
      </div>
    `).join('');
  }
}

// AI Coach Form & Recovery Advisory
async function loadCoachAdvice() {
  try {
    const res = await apiRequest('/coach/advice');
    const adviceEl = document.getElementById('coach-advice-text');
    if (adviceEl && res) {
      adviceEl.innerHTML = res.advice.replace(/\n/g, '<br>');
    }
  } catch (e) {}
}

// Printable PDF Report Download
async function downloadPdfReport() {
  if (!currentToken) {
    showToast('Authentication token required. Please log in.', 'warning');
    showAuthModal(true);
    return;
  }
  showToast('Compiling personalized 4-week coaching dossier via ReportLab...', 'info');
  try {
    const response = await fetch(`/api/reports/download?token=${encodeURIComponent(currentToken)}`, {
      headers: {
        'Authorization': `Bearer ${currentToken}`
      }
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
    showToast('Executive PDF Blueprint downloaded successfully!', 'success');
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// Initialization on DOM Load
document.addEventListener('DOMContentLoaded', () => {
  // Hamburger Drawer Toggles
  const menuBtn = document.getElementById('btn-toggle-menu');
  if (menuBtn) menuBtn.addEventListener('click', () => toggleSidebar(true));
  
  const closeBtn = document.getElementById('btn-close-sidebar');
  if (closeBtn) closeBtn.addEventListener('click', () => toggleSidebar(false));
  
  const overlay = document.getElementById('sidebar-overlay');
  if (overlay) {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) toggleSidebar(false);
    });
  }
  
  // Navigation Links Click Handling
  document.querySelectorAll('.sidebar-nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = link.getAttribute('data-target');
      if (target) navigateTo(target);
    });
  });
  
  // Injury Chip Toggles
  document.querySelectorAll('.injury-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('active');
    });
  });
  
  // Forms
  const profForm = document.getElementById('profile-form');
  if (profForm) profForm.addEventListener('submit', handleProfileSave);
  
  const logForm = document.getElementById('log-set-form');
  if (logForm) logForm.addEventListener('submit', handleSetLog);
  
  const scanForm = document.getElementById('physique-form');
  if (scanForm) scanForm.addEventListener('submit', handlePhysiqueUpload);
  
  // Image preview
  const fileInput = document.getElementById('physique-file');
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
  const authForm = document.getElementById('auth-form');
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
          showToast('Athlete account created! Authenticating...', 'success');
        }
        
        const tokenData = await apiRequest('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password })
        });
        
        currentToken = tokenData.access_token;
        localStorage.setItem('fitmorph_token', currentToken);
        showToast('Authenticated successfully. Welcome to FitMorph!', 'success');
        checkAuth();
      } catch (err) {}
    });
  }
  
  checkAuth();
});
