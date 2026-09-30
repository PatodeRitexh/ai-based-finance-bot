/**
 * Personal Finance Advisor Bot - Income Management Controller
 * Handles CRUD operations for user income streams.
 */

let editingIncomeId = null;

async function loadIncomeData() {
  const month = window.AppState.currentMonth;
  try {
    const data = await apiFetch(`/api/income?month=${month}`);
    if (!data) return;

    const totalEl = document.getElementById("income-month-total");
    if (totalEl) totalEl.textContent = formatINR(data.total);

    const countEl = document.getElementById("income-record-count");
    if (countEl) countEl.textContent = `${data.count} entries`;

    renderIncomeTable(data.items);
  } catch (err) {
    console.error("Failed to load income data:", err);
  }
}

function renderIncomeTable(items) {
  const tbody = document.getElementById("income-table-tbody");
  if (!tbody) return;

  if (!items || items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="empty-state" style="padding: 2.5rem; text-align: center;">
          <p>No income records logged for this month.</p>
          <button class="btn btn-primary btn-sm" onclick="openAddIncomeModal()">Add First Income</button>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items
    .map((item) => {
      return `
        <tr>
          <td style="font-weight: 600; color: #0f172a;">${item.source}</td>
          <td style="font-weight: 600;" class="text-positive">${formatINR(item.amount)}</td>
          <td style="color: #64748b; font-size: 0.8rem;">${item.date}</td>
          <td style="color: #64748b; font-size: 0.8rem;">${item.description || "-"}</td>
          <td style="text-align: right;">
            <button class="btn btn-secondary btn-sm" onclick="openEditIncomeModal(${item.id}, '${escapeHtml(item.source)}', ${item.amount}, '${item.date}', '${escapeHtml(item.description)}')">Edit</button>
            <button class="btn btn-danger btn-sm" onclick="deleteIncomeRecord(${item.id})">Delete</button>
          </td>
        </tr>
      `;
    })
    .join("");
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/'/g, "&#39;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function openAddIncomeModal() {
  editingIncomeId = null;
  const title = document.getElementById("income-modal-title");
  if (title) title.textContent = "Record New Income";

  const form = document.getElementById("income-form");
  if (form) form.reset();

  const dateInput = document.getElementById("income-date");
  if (dateInput) dateInput.value = new Date().toISOString().slice(0, 10);

  openModal("modal-income");
}

function openEditIncomeModal(id, source, amount, dateStr, description) {
  editingIncomeId = id;
  const title = document.getElementById("income-modal-title");
  if (title) title.textContent = "Edit Income Record";

  document.getElementById("income-source").value = source;
  document.getElementById("income-amount").value = amount;
  document.getElementById("income-date").value = dateStr;
  document.getElementById("income-description").value = description;

  openModal("modal-income");
}

async function handleIncomeFormSubmit(e) {
  e.preventDefault();
  const source = document.getElementById("income-source").value.trim();
  const amount = parseFloat(document.getElementById("income-amount").value);
  const dateVal = document.getElementById("income-date").value;
  const description = document.getElementById("income-description").value.trim();

  if (!source || isNaN(amount) || amount <= 0 || !dateVal) {
    showToast("Please provide valid source, positive amount, and date", "error");
    return;
  }

  const payload = { source, amount, date: dateVal, description };

  try {
    if (editingIncomeId) {
      await apiFetch(`/api/income/${editingIncomeId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Income record updated");
    } else {
      await apiFetch("/api/income", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("Income record added");
    }
    closeModal("modal-income");
    loadIncomeData();
  } catch (err) {
    // Handled in apiFetch
  }
}

async function deleteIncomeRecord(id) {
  if (!confirm("Are you sure you want to delete this income entry?")) {
    return;
  }
  try {
    await apiFetch(`/api/income/${id}`, { method: "DELETE" });
    showToast("Income record deleted");
    loadIncomeData();
  } catch (err) {
    // Handled in apiFetch
  }
}

// Bind events on load
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("income-form");
  if (form) {
    form.addEventListener("submit", handleIncomeFormSubmit);
  }
});

window.loadIncomeData = loadIncomeData;
window.openAddIncomeModal = openAddIncomeModal;
window.openEditIncomeModal = openEditIncomeModal;
window.deleteIncomeRecord = deleteIncomeRecord;
