from flask import Blueprint, request, jsonify, session
from services.finance_service import FinanceService
from . import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("", methods=["GET"])
@login_required
def get_dashboard_data():
    """Retrieve full aggregated dashboard statistics for authenticated user."""
    user_id = session["user_id"]
    month = request.args.get("month")

    try:
        summary = FinanceService.get_user_dashboard_summary(user_id, month_str=month)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": f"Failed to compute dashboard metrics: {str(e)}"}), 500
