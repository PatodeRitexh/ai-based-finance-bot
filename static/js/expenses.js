/**
 * Personal Finance Advisor Bot - Expense Management Controller
 * Handles CRUD operations, category filtering, and ledger displays.
 */

let editingExpenseId = null;

async function loadExpenseData() {
  const month = window.AppState.currentMonth;
  const categoryFilter = document.getElementById("expense-category-filter");
  const category = categoryFilter ? categoryFilter.value : "All";

  try {
    const data = await apiFetch(`/api/expenses?month=${month}&category=${category}`);
    if (!data) return;

    const totalEl = document.getElementById("expense-month-total");
    if (totalEl) totalEl.textContent = formatINR(data.total);

    const countEl = document.getElementById("expense-record-count");
    if (countEl) countEl.textContent = `${data.count} entries`;

    renderExpenseTable(data.items);
  } catch (err) {
    console.error("Failed to load expense records:", err);
  }
}

function renderExpenseTable(items) {
  const tbody = document.getElementById("expense-table-tbody");
  if (!tbody) return;

  if (!items || items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="empty-state" style="padding: 2.5rem; text-align: center;">
          <p>No expenses found for this month and category.</p>
          <button class="btn btn-primary btn-sm" onclick="openAddExpenseModal()">Record First Expense</button>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items
    .map((item) => {
      return `
        <tr>
          <td>
            <span class="badge badge-expense">${item.category}</span>
          </td>
          <td style="font-weight: 600; color: #0f172a;">${formatINR(item.amount)}</td>
          <td style="color: #64748b; font-size: 0.8rem;">${item.date}</td>
          <td style="color: #64748b; font-size: 0.8rem;">${item.description || "-"}</td>
          <td style="text-align: right;">
            <button class="btn btn-secondary btn-sm" onclick="openEditExpenseModal(${item.id}, '${escapeHtml(item.category)}', ${item.amount}, '${item.date}', '${escapeHtml(item.description)}')">Edit</button>
            <button class="btn btn-danger btn-sm" onclick="deleteExpenseRecord(${item.id})">Delete</button>
          </td>
        </tr>
      `;
    })
    .join("");
}

function openAddExpenseModal() {
  editingExpenseId = null;
  const title = document.getElementById("expense-modal-title");
  if (title) title.textContent = "Record New Expense";

  const form = document.getElementById("expense-form");
  if (form) form.reset();

  const dateInput = document.getElementById("expense-date");
  if (dateInput) dateInput.value = new Date().toISOString().slice(0, 10);

  openModal("modal-expense");
}

function openEditExpenseModal(id, category, amount, dateStr, description) {
  editingExpenseId = id;
  const title = document.getElementById("expense-modal-title");
  if (title) title.textContent = "Edit Expense Record";

  document.getElementById("expense-category").value = category;
  document.getElementById("expense-amount").value = amount;
  document.getElementById("expense-date").value = dateStr;
  document.getElementById("expense-description").value = description;

  openModal("modal-expense");
}

async function handleExpenseFormSubmit(e) {
  e.preventDefault();
  const category = document.getElementById("expense-category").value;
  const amount = parseFloat(document.getElementById("expense-amount").value);
  const dateVal = document.getElementById("expense-date").value;
  const description = document.getElementById("expense-description").value.trim();

  if (!category || isNaN(amount) || amount <= 0 || !dateVal) {
    showToast("Please provide valid category, positive amount, and date", "error");
    return;
  }

  const payload = { category, amount, date: dateVal, description };

  try {
    if (editingExpenseId) {
      await apiFetch(`/api/expenses/${editingExpenseId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Expense updated successfully");
    } else {
      await apiFetch("/api/expenses", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("Expense recorded successfully");
    }
    closeModal("modal-expense");
    loadExpenseData();
  } catch (err) {
    // Handled in apiFetch
  }
}

async function deleteExpenseRecord(id) {
  if (!confirm("Are you sure you want to delete this expense record?")) {
    return;
  }
  try {
    await apiFetch(`/api/expenses/${id}`, { method: "DELETE" });
    showToast("Expense record removed");
    loadExpenseData();
  } catch (err) {
    // Handled in apiFetch
  }
}

// Bind event listeners
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("expense-form");
  if (form) {
    form.addEventListener("submit", handleExpenseFormSubmit);
  }

  const categoryFilter = document.getElementById("expense-category-filter");
  if (categoryFilter) {
    categoryFilter.addEventListener("change", () => loadExpenseData());
  }
});

window.loadExpenseData = loadExpenseData;
window.openAddExpenseModal = openAddExpenseModal;
window.openEditExpenseModal = openEditExpenseModal;
window.deleteExpenseRecord = deleteExpenseRecord;
