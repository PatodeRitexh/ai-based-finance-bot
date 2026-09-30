from datetime import datetime, date
from flask import Blueprint, request, jsonify, session
from sqlalchemy import extract
from models import db, Expense
from . import login_required

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/expenses")


@expenses_bp.route("", methods=["GET"])
@login_required
def list_expenses():
    """List expenses for authenticated user, with optional month and category filters."""
    user_id = session["user_id"]
    month = request.args.get("month")
    category = request.args.get("category")

    query = Expense.query.filter_by(user_id=user_id)

    if month:
        try:
            yr, mo = map(int, month.split("-"))
            query = query.filter(
                extract("year", Expense.date) == yr,
                extract("month", Expense.date) == mo,
            )
        except ValueError:
            pass

    if category and category.lower() != "all":
        query = query.filter(Expense.category == category)

    records = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total = sum(r.amount for r in records)

    return jsonify({
        "items": [r.to_dict() for r in records],
        "total": float(total),
        "count": len(records),
        "categories": Expense.CATEGORIES,
    }), 200


@expenses_bp.route("", methods=["POST"])
@login_required
def create_expense():
    """Create a new expense record."""
    user_id = session["user_id"]
    data = request.get_json() or {}

    try:
        amount = float(data.get("amount", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid expense amount provided"}), 400

    if amount <= 0:
        return jsonify({"error": "Expense amount must be greater than zero"}), 400

    category = (data.get("category") or "").strip()
    if not category:
        return jsonify({"error": "Category is required"}), 400

    # Match or fallback to Other if category not in standard list
    if category not in Expense.CATEGORIES:
        category = "Other"

    date_str = data.get("date")
    try:
        expense_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400

    description = (data.get("description") or "").strip()

    try:
        record = Expense(
            user_id=user_id,
            amount=amount,
            category=category,
            date=expense_date,
            description=description,
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({"message": "Expense recorded", "item": record.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to record expense: {str(e)}"}), 500


@expenses_bp.route("/<int:expense_id>", methods=["PUT"])
@login_required
def update_expense(expense_id: int):
    """Update an existing expense entry."""
    user_id = session["user_id"]
    record = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not record:
        return jsonify({"error": "Expense record not found"}), 404

    data = request.get_json() or {}

    if "amount" in data:
        try:
            val = float(data["amount"])
            if val <= 0:
                return jsonify({"error": "Amount must be greater than zero"}), 400
            record.amount = val
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount provided"}), 400

    if "category" in data:
        cat = str(data["category"]).strip()
        if cat in Expense.CATEGORIES:
            record.category = cat
        else:
            record.category = "Other"

    if "date" in data:
        try:
            record.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400

    if "description" in data:
        record.description = str(data["description"]).strip()

    try:
        db.session.commit()
        return jsonify({"message": "Expense updated", "item": record.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update expense: {str(e)}"}), 500


@expenses_bp.route("/<int:expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id: int):
    """Delete an expense entry."""
    user_id = session["user_id"]
    record = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not record:
        return jsonify({"error": "Expense record not found"}), 404

    try:
        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Expense deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete expense: {str(e)}"}), 500
