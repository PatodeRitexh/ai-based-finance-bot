/**
 * Personal Finance Advisor Bot - Dashboard Controller
 * Fetches aggregated financial summary and renders Chart.js visualizations.
 */

let categoryChartInstance = null;
let trendChartInstance = null;

async function loadDashboardData() {
  const month = window.AppState.currentMonth;
  try {
    const data = await apiFetch(`/api/dashboard?month=${month}`);
    if (!data) return;

    // 1. Update Core Metric Cards
    const incomeEl = document.getElementById("metric-total-income");
    const expenseEl = document.getElementById("metric-total-expenses");
    const savingsEl = document.getElementById("metric-net-savings");
    const savingsPctEl = document.getElementById("metric-savings-pct");
    const budgetRemainingEl = document.getElementById("metric-budget-remaining");

    if (incomeEl) incomeEl.textContent = formatINR(data.total_income);
    if (expenseEl) expenseEl.textContent = formatINR(data.total_expenses);
    if (savingsEl) {
      savingsEl.textContent = formatINR(data.net_savings);
      savingsEl.className = data.net_savings >= 0 ? "metric-value text-positive" : "metric-value text-negative";
    }
    if (savingsPctEl) {
      savingsPctEl.textContent = `${data.savings_percentage}% of income`;
    }
    if (budgetRemainingEl) {
      budgetRemainingEl.textContent = formatINR(data.total_budget_remaining);
    }

    // 2. Render Expense Breakdown Doughnut Chart
    renderCategoryDoughnutChart(data.category_breakdown);

    // 3. Render 6-Month Income vs Expense Trend Chart
    renderMonthlyTrendChart(data.monthly_trend);

    // 4. Render Recent Transactions Table
    renderRecentTransactions(data.recent_transactions);

    // 5. Update AI Summary Teaser Card
    const aiTeaserEl = document.getElementById("dashboard-ai-summary-text");
    if (aiTeaserEl) {
      if (data.total_income > 0 || data.total_expenses > 0) {
        aiTeaserEl.textContent = `Current savings rate is ${data.savings_percentage}%. Total expenditure recorded across ${Object.keys(data.category_breakdown).length} categories this month. Click below for deep Gemini analysis.`;
      } else {
        aiTeaserEl.textContent = "No financial activity recorded for this period. Add income or expenses to generate Gemini AI insights.";
      }
    }
  } catch (err) {
    console.error("Error loading dashboard metrics:", err);
  }
}

function renderCategoryDoughnutChart(categoryData) {
  const ctx = document.getElementById("chart-category-breakdown");
  if (!ctx) return;

  const categories = Object.keys(categoryData || {});
  const amounts = categories.map((cat) => categoryData[cat].amount);

  // Palette: Emerald, Blue, Amber, Slate, Indigo, Teal, Red, Gray
  const palette = [
    "#059669",
    "#0284c7",
    "#d97706",
    "#475569",
    "#6366f1",
    "#0d9488",
    "#dc2626",
    "#64748b",
    "#84cc16",
  ];

  if (categoryChartInstance) {
    categoryChartInstance.destroy();
  }

  if (categories.length === 0 || amounts.every((a) => a === 0)) {
    // Empty state fallback on canvas
    categoryChartInstance = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["No expenses recorded"],
        datasets: [{ data: [1], backgroundColor: ["#e2e8f0"] }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
      },
    });
    return;
  }

  categoryChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: categories,
      datasets: [
        {
          data: amounts,
          backgroundColor: palette.slice(0, categories.length),
          borderWidth: 1,
          borderColor: "#ffffff",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            boxWidth: 12,
            font: { size: 11, family: "sans-serif" },
            color: "#475569",
          },
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              const val = context.raw || 0;
              return ` ${context.label}: ${formatINR(val)}`;
            },
          },
        },
      },
      cutout: "68%",
    },
  });
}

function renderMonthlyTrendChart(trendData) {
  const ctx = document.getElementById("chart-monthly-trend");
  if (!ctx) return;

  if (trendChartInstance) {
    trendChartInstance.destroy();
  }

  const labels = (trendData && trendData.labels) || [];
  const incomeSeries = (trendData && trendData.income) || [];
  const expenseSeries = (trendData && trendData.expenses) || [];

  trendChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Income",
          data: incomeSeries,
          backgroundColor: "#059669",
          borderRadius: 4,
          barPercentage: 0.6,
        },
        {
          label: "Expenses",
          data: expenseSeries,
          backgroundColor: "#475569",
          borderRadius: 4,
          barPercentage: 0.6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 }, color: "#64748b" },
        },
        y: {
          grid: { color: "#f1f5f9" },
          ticks: {
            font: { size: 11 },
            color: "#64748b",
            callback: function (val) {
              return "₹" + (val >= 1000 ? (val / 1000).toFixed(0) + "k" : val);
            },
          },
        },
      },
      plugins: {
        legend: {
          position: "top",
          align: "end",
          labels: { boxWidth: 12, font: { size: 11 }, color: "#475569" },
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return ` ${context.dataset.label}: ${formatINR(context.raw)}`;
            },
          },
        },
      },
    },
  });
}

function renderRecentTransactions(transactions) {
  const container = document.getElementById("dashboard-recent-transactions-tbody");
  if (!container) return;

  if (!transactions || transactions.length === 0) {
    container.innerHTML = `
      <tr>
        <td colspan="4" class="empty-state" style="padding: 1.5rem; text-align: center;">
          No transactions recorded for this month.
        </td>
      </tr>
    `;
    return;
  }

  container.innerHTML = transactions
    .map((tx) => {
      const isIncome = tx.type === "income";
      const badgeClass = isIncome ? "badge-income" : "badge-expense";
      const amountPrefix = isIncome ? "+₹" : "-₹";
      const formattedAmount = `${amountPrefix}${Number(tx.amount).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`;
      const amountColor = isIncome ? "text-positive" : "text-main";

      return `
        <tr>
          <td>
            <div style="font-weight: 500;">${tx.title}</div>
            <div style="font-size: 0.725rem; color: #64748b;">${tx.description || "No description"}</div>
          </td>
          <td><span class="badge ${badgeClass}">${tx.category}</span></td>
          <td style="color: #64748b; font-size: 0.8rem;">${tx.date}</td>
          <td style="text-align: right; font-weight: 600;" class="${amountColor}">
            ${formattedAmount}
          </td>
        </tr>
      `;
    })
    .join("");
}

// Expose globally
window.loadDashboardData = loadDashboardData;
