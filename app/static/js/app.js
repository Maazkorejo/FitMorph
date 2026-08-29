// FitMorph Frontend Application Engine
const API_BASE = '/api';

// State Management
let currentUser = null;
let currentToken = localStorage.getItem('fitmorph_token') || null;
let activePlan = null;
let activeDayIndex = 0;

// API Helper
async function apiRequest(endpoint, options = {}) {
  const headers = { ...options.headers };
  if (currentToken) {
    headers['Authorization'] = `Bearer ${currentToken}`;
  }
  
  // Don't set Content-Type if sending FormData (browser sets boundary)
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
      showToast('Session expired. Please log in again.', 'warning');
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
  
  let icon = 'ℹ️';
  if (type === 'success') icon = '✅';
  if (type === 'danger') icon = '⚠️';
  if (type === 'warning') icon = '⏳';
  
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

// Tab Switching
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-tab');
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      
      btn.classList.add('active');
      const pane = document.getElementById(target);
      if (pane) pane.classList.add('active');
    });
  });
}

// Authentication Handlers
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
  
  const userDisplay = document.getElementById('nav-user-email');
  if (userDisplay && currentUser) {
    userDisplay.textContent = currentUser.full_name || currentUser.email;
  }
}

function handleLogout() {
  currentToken = null;
  currentUser = null;
  localStorage.removeItem('fitmorph_token');
  showAuthModal(true);
}

function showAuthModal(show = true) {
  const modal = document.getElementById('auth-modal');
  if (modal) {
    if (show) modal.classList.add('open');
    else modal.classList.remove('open');
  }
}

// Profile & Biometrics
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
      
      // Update injury chips
      const injuries = profile.injury_list || [];
      document.querySelectorAll('.injury-chip').forEach(chip => {
        const val = chip.getAttribute('data-injury');
        if (injuries.includes(val)) {
          chip.classList.add('active');
        } else {
          chip.classList.remove('active');
        }
      });
    }
  } catch (e) {
    // 404 means user needs to complete onboarding
  }
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
    showToast('Biometric profile updated successfully!', 'success');
    updateBMIDisplay(profile.bmi, profile.bmi_category);
    loadCoachAdvice();
  } catch (e) {}
}

// Workout Generation & Display
async function handleGenerateWorkout() {
  const btn = document.getElementById('btn-generate-workout');
  if (btn) btn.disabled = true;
  showToast('Synthesizing periodized 4-week split with injury shield...', 'info');
  
  try {
    const plan = await apiRequest('/workouts/generate', {
      method: 'POST',
      body: JSON.stringify({})
    });
    activePlan = plan;
    renderWorkoutPlan(plan);
    showToast('4-Week Blueprint generated successfully!', 'success');
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
  } catch (e) {
    document.getElementById('workout-container').innerHTML = `
      <div style="text-align: center; padding: 3rem 1rem;">
        <p style="color: var(--text-secondary); margin-bottom: 1.25rem;">No active workout generated yet.</p>
        <button class="btn btn-primary" onclick="handleGenerateWorkout()">⚡ Generate 4-Week Blueprint</button>
      </div>
    `;
  }
}

function renderWorkoutPlan(plan) {
  const container = document.getElementById('workout-container');
  if (!container) return;
  
  let daysNav = '<div style="display: flex; gap: 0.5rem; margin-bottom: 1.25rem; overflow-x: auto;">';
  plan.days.forEach((day, idx) => {
    const activeCls = idx === activeDayIndex ? 'btn-primary' : 'btn-secondary';
    daysNav += `<button class="btn ${activeCls} btn-sm" onclick="selectWorkoutDay(${idx})">Day ${day.day_number}</button>`;
  });
  daysNav += '</div>';
  
  const currentDay = plan.days[activeDayIndex] || plan.days[0];
  
  let exercisesHtml = '';
  currentDay.exercises.forEach(ex => {
    const swapBadge = ex.is_swap ? '<span class="badge badge-cyan" style="margin-left: 0.5rem;">SWAPPED</span>' : '';
    exercisesHtml += `
      <div class="exercise-item-card">
        <div class="exercise-meta">
          <div class="exercise-name">
            ${ex.name} ${swapBadge}
          </div>
          <div class="exercise-stats">
            <span><b>Sets:</b> ${ex.sets}</span>
            <span><b>Reps:</b> ${ex.reps}</span>
            <span><b>Rest:</b> ${ex.rest_seconds}s</span>
            <span><b>Target RPE:</b> ${ex.rpe_target}</span>
          </div>
          <div class="exercise-cue">💡 ${ex.cues}</div>
        </div>
        <div>
          <button class="btn btn-secondary btn-sm" onclick="promptExerciseSwap(${currentDay.id}, '${ex.name.replace(/'/g, "\\'")}')">🔄 Swap</button>
        </div>
      </div>
    `;
  });
  
  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
      <div>
        <h3 style="font-size: 1.2rem; font-weight: 800;">${plan.title}</h3>
        <p style="color: var(--text-secondary); font-size: 0.85rem;">Split: ${plan.split_type} | Equipment: ${plan.equipment.replace('_', ' ').toUpperCase()}</p>
      </div>
      <button class="btn btn-primary btn-sm" onclick="handleGenerateWorkout()">🔄 Regenerate</button>
    </div>
    ${daysNav}
    <div style="background: var(--bg-surface-elevated); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 0.85rem 1rem; margin-bottom: 1.25rem;">
      <span style="font-size: 0.8rem; font-weight: 700; color: var(--accent-cyan); text-transform: uppercase;">Prescribed Cardio Protocol:</span>
      <p style="color: var(--text-primary); font-size: 0.9rem; margin-top: 0.2rem;">${currentDay.cardio_protocol}</p>
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

// 1-Click Joint Safe Exercise Swapper
async function promptExerciseSwap(dayId, exerciseName) {
  showToast(`Finding biomechanically safe substitute for "${exerciseName}"...`, 'info');
  try {
    const swapResult = await apiRequest('/workouts/swap', {
      method: 'POST',
      body: JSON.stringify({
        day_id: dayId,
        exercise_name: exerciseName,
        reason: 'joint_discomfort'
      })
    });
    
    showToast(`Replaced with ${swapResult.replacement.name}!`, 'success');
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
    showToast(`Logged set! Volume load: ${logged.volume_load}kg | Est 1RM: ${logged.estimated_one_rep_max}kg`, 'success');
    loadVolumeSummary();
    loadPlateauStatus();
    loadRecentLogs();
  } catch (e) {}
}

async function loadVolumeSummary() {
  try {
    const summary = await apiRequest('/logs/summary');
    if (summary) {
      document.getElementById('stat-total-volume').textContent = `${summary.total_volume_kg.toLocaleString()} kg`;
      document.getElementById('stat-total-sets').textContent = summary.total_sets;
      document.getElementById('stat-total-reps').textContent = summary.total_reps;
      
      const changeEl = document.getElementById('stat-volume-change');
      if (changeEl) {
        changeEl.textContent = `${summary.weekly_change_pct > 0 ? '+' : ''}${summary.weekly_change_pct}%`;
        changeEl.style.color = summary.weekly_change_pct >= 0 ? 'var(--accent-emerald)' : 'var(--danger)';
      }
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
        badge.textContent = 'DELOAD RECOMMENDED';
        badge.className = 'badge badge-amber';
      } else {
        badge.textContent = 'PROGRESSIVE OVERLOAD';
        badge.className = 'badge badge-emerald';
      }
    }
    if (recText) recText.textContent = status.coaching_recommendation;
  } catch (e) {}
}

// AI Vision Physique Scanner
async function handlePhysiqueUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('physique-file');
  const monthInput = document.getElementById('physique-month');
  
  if (!fileInput.files || fileInput.files.length === 0) {
    showToast('Please select a physique photo to upload', 'warning');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('month_number', monthInput.value || 1);
  
  const scanBtn = document.getElementById('btn-scan-physique');
  scanBtn.disabled = true;
  scanBtn.textContent = 'Analyzing Symmetry...';
  showToast('Analyzing muscular symmetry and posture cues...', 'info');
  
  try {
    const scan = await apiRequest('/physique/scan', {
      method: 'POST',
      body: formData
    });
    
    renderPhysiqueScanResult(scan);
    showToast('Physique symmetry analysis complete!', 'success');
  } catch (e) {
  } finally {
    scanBtn.disabled = false;
    scanBtn.textContent = 'Upload & Analyze Photo';
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
      <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 0.65rem 0.85rem; margin-top: 0.4rem;">
        <b>${b.name}</b> (${b.target_muscle}): ${b.sets} sets x ${b.reps} reps
        <div style="font-size: 0.78rem; color: var(--text-muted);">${b.reason}</div>
      </div>
    `).join('');
  }
}

// AI Coach Advice
async function loadCoachAdvice() {
  try {
    const res = await apiRequest('/coach/advice');
    const adviceEl = document.getElementById('coach-advice-text');
    if (adviceEl && res) {
      adviceEl.innerHTML = res.advice.replace(/\n/g, '<br>');
    }
  } catch (e) {}
}

// Download PDF Dossier
async function downloadPdfReport() {
  if (!currentToken) {
    showToast('Please log in first to download your dossier', 'warning');
    showAuthModal(true);
    return;
  }
  showToast('Generating personalized 4-week PDF dossier...', 'info');
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
    showToast('PDF Blueprint downloaded successfully!', 'success');
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// Initialization on DOM load
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  
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
  
  // Login / Signup Form
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
          showToast('Account created! Logging in...', 'success');
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
