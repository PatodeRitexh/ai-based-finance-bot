from flask import Blueprint, request, jsonify, session
from services.finance_service import FinanceService
from services.gemini_service import GeminiService
from . import login_required

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.route("/analyze", methods=["POST"])
@login_required
def analyze_finances():
    """
    Generate Gemini-powered AI financial insights based on the user's live financial data.
    Returns structured recommendations and savings insights.
    """
    user_id = session["user_id"]
    data = request.get_json() or {}
    month = data.get("month") or FinanceService.get_current_month_str()

    try:
        # Retrieve full financial summary for this month
        financial_summary = FinanceService.get_user_dashboard_summary(user_id, month_str=month)

        # Execute Gemini analysis
        analysis_result = GeminiService.analyze_finances(financial_summary)

        return jsonify(analysis_result), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"AI analysis process encountered an error: {str(e)}",
            "disclaimer": "AI-generated information is for educational and planning purposes and should not be considered professional financial advice.",
        }), 500
