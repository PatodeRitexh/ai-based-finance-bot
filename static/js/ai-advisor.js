/**
 * Personal Finance Advisor Bot - AI Advisor Client
 * Interfaces with the Gemini backend endpoint to analyze live financial metrics.
 */

async function runGeminiAnalysis() {
  const container = document.getElementById("ai-advisor-results");
  const button = document.getElementById("btn-run-ai-analysis");
  const month = window.AppState.currentMonth;

  if (button) {
    button.disabled = true;
    button.innerHTML = `
      <svg style="width: 16px; height: 16px; animation: spin 1s linear infinite;" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10" stroke-width="3" stroke-opacity="0.25"></circle>
        <path d="M12 2a10 10 0 0 1 10 10" stroke-width="3"></path>
      </svg>
      Analyzing with Gemini...
    `;
  }

  if (container) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem 1rem; color: #64748b;">
        <p style="font-weight: 500; color: #0f172a; margin-bottom: 0.25rem;">Processing financial data with Gemini AI...</p>
        <p style="font-size: 0.8rem;">Synthesizing monthly cash flow, category distributions, and budget variances.</p>
      </div>
    `;
  }

  try {
    const data = await apiFetch("/api/ai/analyze", {
      method: "POST",
      body: JSON.stringify({ month }),
    });

    if (!data) return;
    renderAIResults(data);
  } catch (err) {
    if (container) {
      container.innerHTML = `
        <div class="card-box" style="padding: 1.5rem; border-color: #fecaca; background-color: #fef2f2;">
          <h4 style="color: #dc2626; margin-bottom: 0.5rem;">Analysis Notice</h4>
          <p style="color: #7f1d1d; font-size: 0.85rem;">${escapeHtml(err.message || "Unable to complete AI assessment.")}</p>
          <button class="btn btn-secondary btn-sm" style="margin-top: 1rem;" onclick="runGeminiAnalysis()">Try Again</button>
        </div>
      `;
    }
  } finally {
    if (button) {
      button.disabled = false;
      button.innerHTML = `
        <svg style="width: 16px; height: 16px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
        </svg>
        Re-Analyze Financials
      `;
    }
  }
}

function renderAIResults(data) {
  const container = document.getElementById("ai-advisor-results");
  if (!container) return;

  const insightsHtml = (data.spending_insights || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  const overspendingHtml = (data.overspending_categories || [])
    .map((item) => {
      const severityClass = item.severity === "high" ? "badge-danger" : "badge-warning";
      return `
        <div style="display: flex; align-items: flex-start; justify-content: space-between; padding: 0.65rem 0; border-bottom: 1px solid #f1f5f9;">
          <div>
            <strong style="color: #0f172a; font-size: 0.85rem;">${escapeHtml(item.category)}</strong>
            <p style="font-size: 0.8rem; color: #475569; margin-top: 0.15rem;">${escapeHtml(item.issue)}</p>
          </div>
          <span class="badge ${severityClass}">${escapeHtml(item.severity || "medium")}</span>
        </div>
      `;
    })
    .join("");

  const recommendationsHtml = (data.budget_recommendations || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  const savingsHtml = (data.saving_suggestions || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  const reductionsHtml = (data.unnecessary_expense_reductions || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");

  let noticeBanner = "";
  if (data.notice) {
    noticeBanner = `
      <div style="background-color: #fffbeb; border: 1px solid #fde68a; color: #92400e; padding: 0.65rem 0.85rem; border-radius: 4px; font-size: 0.775rem; margin-bottom: 1rem;">
        ${escapeHtml(data.notice)}
      </div>
    `;
  }

  container.innerHTML = `
    ${noticeBanner}

    <div class="ai-section-box" style="background-color: #ffffff;">
      <h4>Executive Monthly Cash Flow Summary</h4>
      <p style="font-size: 0.9rem; line-height: 1.6; color: #0f172a;">
        ${escapeHtml(data.monthly_financial_summary || "No summary compiled.")}
      </p>
    </div>

    <div class="dashboard-grid-2" style="margin-bottom: 1rem;">
      <div class="ai-section-box">
        <h4>Key Spending Insights</h4>
        <ul class="ai-list">
          ${insightsHtml || "<li>No specific spending anomalies identified.</li>"}
        </ul>
      </div>

      <div class="ai-section-box">
        <h4>Budget & Overspending Variance</h4>
        <div>
          ${overspendingHtml || '<p style="font-size: 0.85rem; color: #059669; padding: 0.5rem 0;">All monitored categories remain within defined limits.</p>'}
        </div>
      </div>
    </div>

    <div class="dashboard-grid-2" style="margin-bottom: 1rem;">
      <div class="ai-section-box">
        <h4>Budget Optimization Rules</h4>
        <ul class="ai-list">
          ${recommendationsHtml || "<li>Maintain standard 50/30/20 proportions.</li>"}
        </ul>
      </div>

      <div class="ai-section-box">
        <h4>Targeted Savings Accelerators</h4>
        <ul class="ai-list">
          ${savingsHtml || "<li>Automate regular transfers to liquid reserve goals.</li>"}
        </ul>
      </div>
    </div>

    <div class="ai-section-box">
      <h4>Actionable Expense Trimming</h4>
      <ul class="ai-list">
        ${reductionsHtml || "<li>Audit recurring utility and subscription services.</li>"}
      </ul>
    </div>

    <div class="ai-disclaimer">
      <strong>Regulatory & Advisory Disclaimer:</strong>
      ${escapeHtml(data.disclaimer || "AI-generated information is for educational and planning purposes and should not be considered professional financial advice.")}
    </div>
  `;
}

// Global exposure
window.runGeminiAnalysis = runGeminiAnalysis;
