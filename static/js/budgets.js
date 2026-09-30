/**
 * Personal Finance Advisor Bot - Budget Planner Controller
 * Manages category spending limits, tracks variance, and alerts on overruns.
 */

let editingBudgetId = null;

async function loadBudgetData() {
  const month = window.AppState.currentMonth;
  try {
    const data = await apiFetch(`/api/budgets?month=${month}`);
    if (!data) return;

    const totalLimitEl = document.getElementById("budget-total-limit");
    const totalRemainingEl = document.getElementById("budget-total-remaining");

    if (totalLimitEl) totalLimitEl.textContent = formatINR(data.total_budget_limit);
    if (totalRemainingEl) totalRemainingEl.textContent = formatINR(data.total_budget_remaining);

    renderBudgetComparison(data.comparison);
  } catch (err) {
    console.error("Failed to load budgets:", err);
  }
}

function renderBudgetComparison(comparisons) {
  const container = document.getElementById("budget-cards-container");
  if (!container) return;

  if (!comparisons || comparisons.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1; padding: 3rem;">
        <p>No budgets configured for this month.</p>
        <button class="btn btn-primary" onclick="openSetBudgetModal()">Set First Category Budget</button>
      </div>
    `;
    return;
  }

  container.innerHTML = comparisons
    .map((item) => {
      const pct = Math.min(100, item.percentage_used);
      let statusBadge = "";
      let progressClass = "";

      if (item.status === "exceeded") {
        statusBadge = '<span class="badge badge-danger">Exceeded</span>';
        progressClass = "danger";
      } else if (item.status === "warning") {
        statusBadge = '<span class="badge badge-warning">Approaching Limit</span>';
        progressClass = "warning";
      } else if (item.status === "unbudgeted") {
        statusBadge = '<span class="badge badge-expense">Unbudgeted</span>';
      } else {
        statusBadge = '<span class="badge badge-success">On Track</span>';
      }

      return `
        <div class="card-box" style="margin-bottom: 0;">
          <div class="card-box-header" style="padding: 0.85rem 1rem;">
            <div>
              <h4 style="font-weight: 600;">${item.category}</h4>
              <div style="font-size: 0.725rem; color: #64748b; margin-top: 0.15rem;">
                Limit: ${formatINR(item.limit)}
              </div>
            </div>
            ${statusBadge}
          </div>
          <div class="card-box-body" style="padding: 1rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.825rem; margin-bottom: 0.4rem;">
              <span>Spent: <strong>${formatINR(item.spent)}</strong></span>
              <span>Remaining: <strong>${formatINR(item.remaining)}</strong></span>
            </div>
            <div class="progress-track" style="margin-bottom: 0.75rem;">
              <div class="progress-fill ${progressClass}" style="width: ${pct}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.75rem; color: #64748b;">${item.percentage_used}% utilized</span>
              <button class="btn btn-secondary btn-sm" onclick="openSetBudgetModal('${item.category}', ${item.limit})">Adjust Limit</button>
            </div>
          </div>
        </div>
      `;
    })
    .join("");
}

function openSetBudgetModal(category = "", currentLimit = "") {
  const form = document.getElementById("budget-form");
  if (form) form.reset();

  const catSelect = document.getElementById("budget-category");
  const limitInput = document.getElementById("budget-limit");

  if (catSelect && category) {
    catSelect.value = category;
  }
  if (limitInput && currentLimit) {
    limitInput.value = currentLimit;
  }

  openModal("modal-budget");
}

async function handleBudgetFormSubmit(e) {
  e.preventDefault();
  const category = document.getElementById("budget-category").value;
  const limit = parseFloat(document.getElementById("budget-limit").value);
  const month = window.AppState.currentMonth;

  if (!category || isNaN(limit) || limit <= 0) {
    showToast("Please select category and enter a valid positive budget limit", "error");
    return;
  }

  try {
    await apiFetch("/api/budgets", {
      method: "POST",
      body: JSON.stringify({ category, limit, month }),
    });
    showToast(`Budget limit updated for ${category}`);
    closeModal("modal-budget");
    loadBudgetData();
  } catch (err) {
    // Handled in apiFetch
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("budget-form");
  if (form) {
    form.addEventListener("submit", handleBudgetFormSubmit);
  }
});

window.loadBudgetData = loadBudgetData;
window.openSetBudgetModal = openSetBudgetModal;
