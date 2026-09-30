from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models import db, SavingsGoal
from . import login_required

goals_bp = Blueprint("goals", __name__, url_prefix="/api/goals")


@goals_bp.route("", methods=["GET"])
@login_required
def list_goals():
    """Retrieve all savings goals for the authenticated user."""
    user_id = session["user_id"]
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.target_date.asc()).all()

    items = [g.to_dict() for g in goals]
    total_target = sum(g["target_amount"] for g in items)
    total_saved = sum(g["current_amount"] for g in items)
    overall_progress = (
        round((total_saved / total_target) * 100.0, 2) if total_target > 0 else 0.0
    )

    return jsonify({
        "items": items,
        "total_target": total_target,
        "total_saved": total_saved,
        "overall_progress_percentage": overall_progress,
        "count": len(items),
    }), 200


@goals_bp.route("", methods=["POST"])
@login_required
def create_goal():
    """Create a new savings goal."""
    user_id = session["user_id"]
    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Goal name is required"}), 400

    try:
        target_amount = float(data.get("target_amount", 0))
        if target_amount <= 0:
            return jsonify({"error": "Target amount must be greater than zero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid target amount provided"}), 400

    try:
        current_amount = float(data.get("current_amount", 0))
        if current_amount < 0:
            current_amount = 0.0
    except (ValueError, TypeError):
        current_amount = 0.0

    target_date_str = data.get("target_date")
    if not target_date_str:
        return jsonify({"error": "Target date is required"}), 400

    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400

    try:
        goal = SavingsGoal(
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date,
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({"message": "Savings goal created", "goal": goal.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create savings goal: {str(e)}"}), 500


@goals_bp.route("/<int:goal_id>", methods=["PUT"])
@login_required
def update_goal(goal_id: int):
    """Update an existing savings goal."""
    user_id = session["user_id"]
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()

    if not goal:
        return jsonify({"error": "Savings goal not found"}), 404

    data = request.get_json() or {}

    if "name" in data:
        name = str(data["name"]).strip()
        if not name:
            return jsonify({"error": "Goal name cannot be empty"}), 400
        goal.name = name

    if "target_amount" in data:
        try:
            val = float(data["target_amount"])
            if val <= 0:
                return jsonify({"error": "Target amount must be greater than zero"}), 400
            goal.target_amount = val
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid target amount provided"}), 400

    if "current_amount" in data:
        try:
            val = float(data["current_amount"])
            if val < 0:
                val = 0.0
            goal.current_amount = val
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid current amount provided"}), 400

    if "target_date" in data:
        try:
            goal.target_date = datetime.strptime(data["target_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400

    try:
        db.session.commit()
        return jsonify({"message": "Goal updated", "goal": goal.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update goal: {str(e)}"}), 500


@goals_bp.route("/<int:goal_id>/deposit", methods=["POST"])
@login_required
def deposit_to_goal(goal_id: int):
    """Contribute money towards a savings goal."""
    user_id = session["user_id"]
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()

    if not goal:
        return jsonify({"error": "Savings goal not found"}), 404

    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            return jsonify({"error": "Deposit amount must be greater than zero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid deposit amount provided"}), 400

    try:
        goal.current_amount += amount
        db.session.commit()
        return jsonify({
            "message": f"Added ₹{amount:,.2f} towards {goal.name}",
            "goal": goal.to_dict(),
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to deposit to goal: {str(e)}"}), 500


@goals_bp.route("/<int:goal_id>", methods=["DELETE"])
@login_required
def delete_goal(goal_id: int):
    """Delete a savings goal."""
    user_id = session["user_id"]
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()

    if not goal:
        return jsonify({"error": "Savings goal not found"}), 404

    try:
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"message": "Savings goal deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete goal: {str(e)}"}), 500
