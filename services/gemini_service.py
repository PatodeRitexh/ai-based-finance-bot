import json
import logging
import os
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "AI-generated information is for educational and planning purposes and "
    "should not be considered professional financial advice."
)


class GeminiService:
    """
    Service wrapper for Google Gemini API integration.
    Analyzes user financial data and generates structured financial planning insights.
    """

    @classmethod
    def get_api_key(cls) -> str:
        """Fetch Gemini API key from environment variable."""
        return os.environ.get("GEMINI_API_KEY", "").strip()

    @classmethod
    def get_model_name(cls) -> str:
        """Fetch configured model name or fallback."""
        return os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()

    @classmethod
    def analyze_finances(cls, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send user financial metrics to Gemini and return structured insights.
        If Gemini is unavailable or errors occur, returns a deterministic fallback.
        """
        api_key = cls.get_api_key()

        if not api_key or api_key == "your_gemini_api_key_here":
            return cls._build_fallback_analysis(
                financial_data,
                reason="GEMINI_API_KEY is not configured in .env. Showing local baseline calculation.",
            )

        # Construct concise, structured financial prompt
        prompt = cls._build_prompt(financial_data)

        # Attempt call via official google-genai SDK
        for attempt in range(2):
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=api_key)
                model_name = cls.get_model_name()

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=2048,
                    ),
                )

                raw_text = response.text or ""
                parsed = cls._parse_ai_response(raw_text, financial_data)
                parsed["source"] = "gemini"
                parsed["disclaimer"] = DISCLAIMER_TEXT
                return parsed

            except Exception as e:
                logger.warning(f"Gemini call attempt {attempt+1} failed: {e}")
                if attempt == 0:
                    import time
                    time.sleep(1.5)
                else:
                    return cls._build_fallback_analysis(
                        financial_data,
                        reason=f"Gemini API returned status notice: {str(e)[:120]}. Displaying rule-based financial analysis.",
                    )

    @classmethod
    def _build_prompt(cls, data: Dict[str, Any]) -> str:
        """Construct a structured prompt with exact financial numbers in INR."""
        income = data.get("total_income", 0.0)
        expenses = data.get("total_expenses", 0.0)
        savings = data.get("net_savings", 0.0)
        savings_pct = data.get("savings_percentage", 0.0)
        categories = data.get("category_breakdown", {})
        budget_comp = data.get("budget_comparison", [])
        goals = data.get("savings_goals", {}).get("items", [])

        cat_summary = ", ".join([f"{k}: ₹{v.get('amount', 0):,.2f}" for k, v in categories.items()])
        if not cat_summary:
            cat_summary = "No expense records yet"

        budget_summary = []
        for b in budget_comp:
            status_flag = b.get("status")
            budget_summary.append(
                f"{b.get('category')}: Limit ₹{b.get('limit', 0):,.0f}, Spent ₹{b.get('spent', 0):,.0f} ({status_flag})"
            )
        budget_str = "; ".join(budget_summary) if budget_summary else "No budgets configured"

        goals_summary = []
        for g in goals:
            goals_summary.append(
                f"{g.get('name')}: Saved ₹{g.get('current_amount', 0):,.0f} / Target ₹{g.get('target_amount', 0):,.0f} ({g.get('progress_percentage', 0)}%)"
            )
        goals_str = "; ".join(goals_summary) if goals_summary else "No active savings goals"

        return f"""You are a personal finance analysis assistant. Analyze the user's monthly financial ledger. All values are in Indian Rupees (INR, ₹).
Rules:
1. Provide actionable, concise advice grounded in practical financial management (such as the 50/30/20 rule, emergency funds, and disciplined budgeting).
2. Do NOT use fake emojis, do NOT use vague AI cliches, do NOT use em dashes.
3. Do NOT provide automated investment trading or speculative stock picks.
4. Output valid JSON only, matching the exact JSON schema below.

User Financial Summary:
- Monthly Income: ₹{income:,.2f}
- Monthly Expenses: ₹{expenses:,.2f}
- Net Monthly Savings: ₹{savings:,.2f} ({savings_pct}% savings rate)
- Category Breakdown: {cat_summary}
- Budgets: {budget_str}
- Goals: {goals_str}

Respond with ONLY valid JSON with this exact schema:
{{
  "monthly_financial_summary": "2-3 sentences summarizing current cashflow status.",
  "spending_insights": [
    "Insight item 1",
    "Insight item 2",
    "Insight item 3"
  ],
  "overspending_categories": [
    {{"category": "CategoryName", "issue": "Specific explanation with numbers", "severity": "high/medium/low"}}
  ],
  "budget_recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ],
  "saving_suggestions": [
    "Saving action 1",
    "Saving action 2"
  ],
  "unnecessary_expense_reductions": [
    "Reduction idea 1",
    "Reduction idea 2"
  ]
}}"""

    @classmethod
    def _parse_ai_response(cls, raw_text: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Safely parse AI response into structured dictionary."""
        cleaned = raw_text.strip()
        # Remove markdown code fence if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            # Ensure all required keys exist
            return {
                "status": "success",
                "monthly_financial_summary": data.get("monthly_financial_summary", "Summary compiled."),
                "spending_insights": data.get("spending_insights", []),
                "overspending_categories": data.get("overspending_categories", []),
                "budget_recommendations": data.get("budget_recommendations", []),
                "saving_suggestions": data.get("saving_suggestions", []),
                "unnecessary_expense_reductions": data.get("unnecessary_expense_reductions", []),
            }
        except json.JSONDecodeError:
            logger.warning("Failed to decode Gemini JSON output directly. Extracting JSON block.")
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                    return {
                        "status": "success",
                        "monthly_financial_summary": data.get("monthly_financial_summary", ""),
                        "spending_insights": data.get("spending_insights", []),
                        "overspending_categories": data.get("overspending_categories", []),
                        "budget_recommendations": data.get("budget_recommendations", []),
                        "saving_suggestions": data.get("saving_suggestions", []),
                        "unnecessary_expense_reductions": data.get("unnecessary_expense_reductions", []),
                    }
                except Exception:
                    pass

            return cls._build_fallback_analysis(financial_data, reason="AI returned non-JSON text. Displaying baseline analysis.")

    @classmethod
    def _build_fallback_analysis(cls, data: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
        """Deterministic rule-based financial analysis when Gemini API is unavailable."""
        income = data.get("total_income", 0.0)
        expenses = data.get("total_expenses", 0.0)
        savings = data.get("net_savings", 0.0)
        savings_pct = data.get("savings_percentage", 0.0)
        categories = data.get("category_breakdown", {})
        budget_comp = data.get("budget_comparison", [])

        # Check overspending
        overspending = []
        for b in budget_comp:
            if b.get("status") == "exceeded":
                overspending.append({
                    "category": b.get("category"),
                    "issue": f"Exceeded allocated limit of ₹{b.get('limit', 0):,.0f} by ₹{abs(b.get('remaining', 0)):,.0f}.",
                    "severity": "high",
                })
            elif b.get("status") == "warning":
                overspending.append({
                    "category": b.get("category"),
                    "issue": f"Utilized {b.get('percentage_used')}% of monthly limit.",
                    "severity": "medium",
                })

        # Summary calculation
        if income == 0 and expenses == 0:
            summary = "No transactions have been recorded for this month yet. Start by logging your monthly income and daily expenses."
        elif savings_pct >= 20.0:
            summary = f"Healthy monthly cash flow. You are currently saving {savings_pct}% of your income (₹{savings:,.2f}), which exceeds the standard 20% savings benchmark."
        elif savings > 0:
            summary = f"Positive cash flow with a {savings_pct}% savings rate. Increasing savings to at least 20% of your ₹{income:,.2f} income will accelerate goal completion."
        else:
            summary = f"Monthly expenses exceed income by ₹{abs(savings):,.2f}. Immediate expense trimming is recommended to avoid cash reserves depletion."

        # Spending insights
        insights = []
        if income > 0:
            needs_estimate = income * 0.50
            if expenses > needs_estimate:
                insights.append(f"Total expenditure (₹{expenses:,.2f}) exceeds 50% of monthly income. Review discretionary allocations.")
            else:
                insights.append(f"Fixed and variable expenditures remain within 50% of your earnings.")
        
        # Find top expense category
        sorted_cats = sorted(categories.values(), key=lambda x: x.get("amount", 0), reverse=True)
        if sorted_cats:
            top = sorted_cats[0]
            insights.append(f"Your highest spending area is {top.get('category')} at ₹{top.get('amount', 0):,.2f} ({top.get('percentage_of_expenses')}% of total spend).")

        insights.append("Maintain an emergency fund balance equivalent to 3 to 6 months of mandatory living expenses.")

        # Recommendations
        recommendations = [
            "Structure monthly allocations around the 50/30/20 guideline (50% essentials, 30% discretionary, 20% savings).",
            "Set explicit monthly spending caps for flexible categories like Dining, Shopping, and Entertainment.",
        ]

        savings_suggestions = [
            "Automate recurring transfers to a dedicated savings or liquid reserve account immediately on salary credit day.",
            "Prioritize funding your Emergency Fund target before expanding non-essential discretionary expenditures.",
        ]

        reductions = [
            "Audit recurring subscriptions and monthly service renewals for unused memberships.",
            "Limit high-frequency ordering on food delivery and quick-commerce platforms.",
        ]

        return {
            "status": "success",
            "source": "rule_engine",
            "notice": reason,
            "monthly_financial_summary": summary,
            "spending_insights": insights,
            "overspending_categories": overspending,
            "budget_recommendations": recommendations,
            "saving_suggestions": savings_suggestions,
            "unnecessary_expense_reductions": reductions,
            "disclaimer": DISCLAIMER_TEXT,
        }
