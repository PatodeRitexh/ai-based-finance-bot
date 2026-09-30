/**
 * Personal Finance Advisor Bot - Savings Goals Controller
 * Tracks target milestones, deposit contributions, and progress tracking.
 */

let activeGoalIdForDeposit = null;
let editingGoalId = null;

async function loadGoalsData() {
  try {
    const data = await apiFetch("/api/goals");
    if (!data) return;

    const totalTargetEl = document.getElementById("goals-total-target");
    const totalSavedEl = document.getElementById("goals-total-saved");
    const overallPctEl = document.getElementById("goals-overall-pct");

    if (totalTargetEl) totalTargetEl.textContent = formatINR(data.total_target);
    if (totalSavedEl) totalSavedEl.textContent = formatINR(data.total_saved);
    if (overallPctEl) overallPctEl.textContent = `${data.overall_progress_percentage}% achieved`;

    renderGoalsGrid(data.items);
  } catch (err) {
    console.error("Failed to load savings goals:", err);
  }
}

function renderGoalsGrid(items) {
  const container = document.getElementById("goals-cards-container");
  if (!container) return;

  if (!items || items.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1; padding: 3rem;">
        <p>No savings targets active yet.</p>
        <button class="btn btn-primary" onclick="openAddGoalModal()">Create Your First Goal</button>
      </div>
    `;
    return;
  }

  container.innerHTML = items
    .map((goal) => {
      const pct = Math.min(100, goal.progress_percentage);
      const isCompleted = pct >= 100;
      const statusBadge = isCompleted
        ? '<span class="badge badge-success">Completed</span>'
        : `<span class="badge badge-expense">${goal.progress_percentage}% Saved</span>`;

      return `
        <div class="card-box" style="margin-bottom: 0;">
          <div class="card-box-header" style="padding: 1rem 1.25rem;">
            <div>
              <h4 style="font-weight: 600;">${goal.name}</h4>
              <div style="font-size: 0.725rem; color: #64748b; margin-top: 0.15rem;">
                Target Date: ${goal.target_date || "Not set"}
              </div>
            </div>
            ${statusBadge}
          </div>
          <div class="card-box-body" style="padding: 1.25rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.825rem; margin-bottom: 0.4rem;">
              <span>Saved: <strong class="text-positive">${formatINR(goal.current_amount)}</strong></span>
              <span>Target: <strong>${formatINR(goal.target_amount)}</strong></span>
            </div>
            <div class="progress-track" style="margin-bottom: 0.75rem; height: 9px;">
              <div class="progress-fill" style="width: ${pct}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; font-size: 0.75rem; color: #64748b;">
              <span>Remaining: ${formatINR(goal.remaining_amount)}</span>
            </div>
            <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
              <button class="btn btn-primary btn-sm" onclick="openDepositModal(${goal.id}, '${escapeHtml(goal.name)}')">+ Add Funds</button>
              <button class="btn btn-secondary btn-sm" onclick="openEditGoalModal(${goal.id}, '${escapeHtml(goal.name)}', ${goal.target_amount}, ${goal.current_amount}, '${goal.target_date}')">Edit</button>
              <button class="btn btn-danger btn-sm" onclick="deleteGoalRecord(${goal.id})">Delete</button>
            </div>
          </div>
        </div>
      `;
    })
    .join("");
}

function openAddGoalModal() {
  editingGoalId = null;
  const title = document.getElementById("goal-modal-title");
  if (title) title.textContent = "Create Savings Target";

  const form = document.getElementById("goal-form");
  if (form) form.reset();

  openModal("modal-goal");
}

function openEditGoalModal(id, name, target, current, targetDate) {
  editingGoalId = id;
  const title = document.getElementById("goal-modal-title");
  if (title) title.textContent = "Edit Savings Goal";

  document.getElementById("goal-name").value = name;
  document.getElementById("goal-target-amount").value = target;
  document.getElementById("goal-current-amount").value = current;
  document.getElementById("goal-target-date").value = targetDate;

  openModal("modal-goal");
}

async function handleGoalFormSubmit(e) {
  e.preventDefault();
  const name = document.getElementById("goal-name").value.trim();
  const target_amount = parseFloat(document.getElementById("goal-target-amount").value);
  const current_amount = parseFloat(document.getElementById("goal-current-amount").value) || 0;
  const target_date = document.getElementById("goal-target-date").value;

  if (!name || isNaN(target_amount) || target_amount <= 0 || !target_date) {
    showToast("Please provide goal name, positive target amount, and target date", "error");
    return;
  }

  const payload = { name, target_amount, current_amount, target_date };

  try {
    if (editingGoalId) {
      await apiFetch(`/api/goals/${editingGoalId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Savings target updated");
    } else {
      await apiFetch("/api/goals", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("Savings target created");
    }
    closeModal("modal-goal");
    loadGoalsData();
  } catch (err) {
    // Handled in apiFetch
  }
}

function openDepositModal(goalId, goalName) {
  activeGoalIdForDeposit = goalId;
  const label = document.getElementById("deposit-goal-name-text");
  if (label) label.textContent = `Contribute to: ${goalName}`;

  const input = document.getElementById("deposit-amount-input");
  if (input) input.value = "";

  openModal("modal-deposit");
}

async function handleDepositSubmit(e) {
  e.preventDefault();
  if (!activeGoalIdForDeposit) return;

  const amount = parseFloat(document.getElementById("deposit-amount-input").value);
  if (isNaN(amount) || amount <= 0) {
    showToast("Please enter a valid deposit amount", "error");
    return;
  }

  try {
    await apiFetch(`/api/goals/${activeGoalIdForDeposit}/deposit`, {
      method: "POST",
      body: JSON.stringify({ amount }),
    });
    showToast(`Added ${formatINR(amount)} to goal`);
    closeModal("modal-deposit");
    loadGoalsData();
  } catch (err) {
    // Handled in apiFetch
  }
}

async function deleteGoalRecord(id) {
  if (!confirm("Are you sure you want to delete this savings goal?")) {
    return;
  }
  try {
    await apiFetch(`/api/goals/${id}`, { method: "DELETE" });
    showToast("Savings goal removed");
    loadGoalsData();
  } catch (err) {
    // Handled in apiFetch
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("goal-form");
  if (form) {
    form.addEventListener("submit", handleGoalFormSubmit);
  }
  const depositForm = document.getElementById("deposit-form");
  if (depositForm) {
    depositForm.addEventListener("submit", handleDepositSubmit);
  }
});

window.loadGoalsData = loadGoalsData;
window.openAddGoalModal = openAddGoalModal;
window.openEditGoalModal = openEditGoalModal;
window.openDepositModal = openDepositModal;
window.deleteGoalRecord = deleteGoalRecord;
