/**
 * Personal Finance Advisor Bot - Core Application Client
 * Provides global currency formatting (INR), toast notifications, modal controls, and tab routing.
 */

// Global State
window.AppState = {
  currentMonth: new Date().toISOString().slice(0, 7), // "YYYY-MM"
  currentUser: null,
  activeTab: "dashboard",
};

/**
 * Format a numeric amount into Indian Rupee format (e.g. ₹1,50,000.00).
 */
function formatINR(amount) {
  if (amount === undefined || amount === null || isNaN(amount)) {
    return "₹0.00";
  }
  const isNegative = amount < 0;
  const absAmount = Math.abs(Number(amount));
  const parts = absAmount.toFixed(2).split(".");
  let intPart = parts[0];
  const decPart = parts[1];

  let formattedInt = "";
  if (intPart.length <= 3) {
    formattedInt = intPart;
  } else {
    const last3 = intPart.substring(intPart.length - 3);
    const rest = intPart.substring(0, intPart.length - 3);
    const chunks = [];
    let r = rest;
    while (r.length > 2) {
      chunks.unshift(r.slice(-2));
      r = r.slice(0, -2);
    }
    if (r.length > 0) {
      chunks.unshift(r);
    }
    formattedInt = chunks.join(",") + "," + last3;
  }

  return (isNegative ? "-₹" : "₹") + formattedInt + "." + decPart;
}

/**
 * Global fetch wrapper with standard JSON parsing and 401 handling.
 */
async function apiFetch(url, options = {}) {
  const defaultHeaders = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  options.headers = { ...defaultHeaders, ...options.headers };

  try {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (response.status === 401) {
      // Redirect to login if unauthenticated
      window.location.href = "/login";
      return null;
    }

    if (!response.ok) {
      const errorMsg = data.error || `HTTP error ${response.status}`;
      throw new Error(errorMsg);
    }

    return data;
  } catch (err) {
    showToast(err.message || "An unexpected error occurred", "error");
    throw err;
  }
}

/**
 * Display toast notification.
 */
function showToast(message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.2s ease";
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

/**
 * Modal Management
 */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("active");
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("active");
  }
}

// Close modals when clicking overlay background
document.addEventListener("click", (e) => {
  if (e.target.classList && e.target.classList.contains("modal-overlay")) {
    e.target.classList.remove("active");
  }
});

/**
 * Tab Navigation
 */
function switchTab(tabName) {
  window.AppState.activeTab = tabName;

  // Update sidebar links
  document.querySelectorAll(".sidebar-nav .nav-link").forEach((link) => {
    if (link.getAttribute("data-tab") === tabName) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });

  // Update view visibility
  document.querySelectorAll(".tab-view").forEach((view) => {
    if (view.id === `view-${tabName}`) {
      view.classList.add("active");
    } else {
      view.classList.remove("active");
    }
  });

  // Update top bar title
  const titleEl = document.getElementById("page-title-text");
  const tabTitles = {
    dashboard: "Financial Overview",
    income: "Income Ledger",
    expenses: "Expense Tracker",
    budgets: "Monthly Budgets",
    goals: "Savings Targets",
    "ai-advisor": "Gemini AI Advisor",
    settings: "System & Profile Settings",
  };
  if (titleEl && tabTitles[tabName]) {
    titleEl.textContent = tabTitles[tabName];
  }

  // Trigger view data refreshes
  if (tabName === "dashboard" && window.loadDashboardData) {
    window.loadDashboardData();
  } else if (tabName === "income" && window.loadIncomeData) {
    window.loadIncomeData();
  } else if (tabName === "expenses" && window.loadExpenseData) {
    window.loadExpenseData();
  } else if (tabName === "budgets" && window.loadBudgetData) {
    window.loadBudgetData();
  } else if (tabName === "goals" && window.loadGoalsData) {
    window.loadGoalsData();
  }
}

// Global initialization
document.addEventListener("DOMContentLoaded", () => {
  // Bind navigation links
  document.querySelectorAll(".sidebar-nav .nav-link[data-tab]").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const tab = link.getAttribute("data-tab");
      switchTab(tab);
    });
  });

  // Month selector synchronization
  const monthInput = document.getElementById("global-month-picker");
  if (monthInput) {
    monthInput.value = window.AppState.currentMonth;
    monthInput.addEventListener("change", (e) => {
      window.AppState.currentMonth = e.target.value;
      // Refresh active view
      switchTab(window.AppState.activeTab);
    });
  }
});
