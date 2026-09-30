from flask import Blueprint, request, jsonify, session
from models import db, Budget, Expense
from services.finance_service import FinanceService
from . import login_required

budgets_bp = Blueprint("budgets", __name__, url_prefix="/api/budgets")


@budgets_bp.route("", methods=["GET"])
@login_required
def list_budgets():
    """Retrieve monthly category budgets and actual spending comparison."""
    user_id = session["user_id"]
    month = request.args.get("month") or FinanceService.get_current_month_str()

    budgets = Budget.query.filter_by(user_id=user_id, month=month).all()
    dashboard_summary = FinanceService.get_user_dashboard_summary(user_id, month_str=month)

    return jsonify({
        "month": month,
        "budgets": [b.to_dict() for b in budgets],
        "comparison": dashboard_summary.get("budget_comparison", []),
        "total_budget_limit": dashboard_summary.get("total_budget_limit", 0.0),
        "total_budget_remaining": dashboard_summary.get("total_budget_remaining", 0.0),
        "available_categories": Expense.CATEGORIES,
    }), 200


@budgets_bp.route("", methods=["POST"])
@login_required
def set_budget():
    """Create or update a budget limit for a category in a specific month."""
    user_id = session["user_id"]
    data = request.get_json() or {}

    category = (data.get("category") or "").strip()
    month = (data.get("month") or FinanceService.get_current_month_str()).strip()

    if not category:
        return jsonify({"error": "Category is required"}), 400

    try:
        limit = float(data.get("limit", 0))
        if limit <= 0:
            return jsonify({"error": "Budget limit must be greater than zero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid budget limit provided"}), 400

    # Look for existing budget for this user, month, and category
    budget = Budget.query.filter_by(user_id=user_id, month=month, category=category).first()

    try:
        if budget:
            budget.limit = limit
            status_code = 200
            msg = f"Budget limit updated for {category}"
        else:
            budget = Budget(user_id=user_id, month=month, category=category, limit=limit)
            db.session.add(budget)
            status_code = 201
            msg = f"Budget limit created for {category}"

        db.session.commit()
        return jsonify({"message": msg, "budget": budget.to_dict()}), status_code
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save budget: {str(e)}"}), 500


@budgets_bp.route("/<int:budget_id>", methods=["PUT"])
@login_required
def update_budget(budget_id: int):
    """Update an existing budget record."""
    user_id = session["user_id"]
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()

    if not budget:
        return jsonify({"error": "Budget record not found"}), 404

    data = request.get_json() or {}

    if "limit" in data:
        try:
            val = float(data["limit"])
            if val <= 0:
                return jsonify({"error": "Limit must be greater than zero"}), 400
            budget.limit = val
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid limit provided"}), 400

    try:
        db.session.commit()
        return jsonify({"message": "Budget updated", "budget": budget.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update budget: {str(e)}"}), 500


@budgets_bp.route("/<int:budget_id>", methods=["DELETE"])
@login_required
def delete_budget(budget_id: int):
    """Delete a budget category limit."""
    user_id = session["user_id"]
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()

    if not budget:
        return jsonify({"error": "Budget record not found"}), 404

    try:
        db.session.delete(budget)
        db.session.commit()
        return jsonify({"message": "Budget limit deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete budget: {str(e)}"}), 500
