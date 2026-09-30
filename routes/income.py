from datetime import datetime, date
from flask import Blueprint, request, jsonify, session
from sqlalchemy import extract
from models import db, Income
from . import login_required

income_bp = Blueprint("income", __name__, url_prefix="/api/income")


@income_bp.route("", methods=["GET"])
@login_required
def list_income():
    """List income records for the authenticated user, optionally filtered by month."""
    user_id = session["user_id"]
    month = request.args.get("month")

    query = Income.query.filter_by(user_id=user_id)

    if month:
        try:
            yr, mo = map(int, month.split("-"))
            query = query.filter(
                extract("year", Income.date) == yr,
                extract("month", Income.date) == mo,
            )
        except ValueError:
            pass

    records = query.order_by(Income.date.desc(), Income.id.desc()).all()
    total = sum(r.amount for r in records)

    return jsonify({
        "items": [r.to_dict() for r in records],
        "total": float(total),
        "count": len(records),
    }), 200


@income_bp.route("", methods=["POST"])
@login_required
def create_income():
    """Add a new income entry."""
    user_id = session["user_id"]
    data = request.get_json() or {}

    try:
        amount = float(data.get("amount", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount provided"}), 400

    if amount <= 0:
        return jsonify({"error": "Income amount must be greater than zero"}), 400

    source = (data.get("source") or "").strip()
    if not source:
        return jsonify({"error": "Income source is required"}), 400

    date_str = data.get("date")
    try:
        income_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400

    description = (data.get("description") or "").strip()

    try:
        record = Income(
            user_id=user_id,
            amount=amount,
            source=source,
            date=income_date,
            description=description,
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({"message": "Income record added", "item": record.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save income: {str(e)}"}), 500


@income_bp.route("/<int:income_id>", methods=["PUT"])
@login_required
def update_income(income_id: int):
    """Update an existing income entry."""
    user_id = session["user_id"]
    record = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not record:
        return jsonify({"error": "Income record not found"}), 404

    data = request.get_json() or {}

    if "amount" in data:
        try:
            val = float(data["amount"])
            if val <= 0:
                return jsonify({"error": "Amount must be greater than zero"}), 400
            record.amount = val
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount provided"}), 400

    if "source" in data:
        source = str(data["source"]).strip()
        if not source:
            return jsonify({"error": "Source cannot be empty"}), 400
        record.source = source

    if "date" in data:
        try:
            record.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400

    if "description" in data:
        record.description = str(data["description"]).strip()

    try:
        db.session.commit()
        return jsonify({"message": "Income record updated", "item": record.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update income: {str(e)}"}), 500


@income_bp.route("/<int:income_id>", methods=["DELETE"])
@login_required
def delete_income(income_id: int):
    """Delete an income entry."""
    user_id = session["user_id"]
    record = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not record:
        return jsonify({"error": "Income record not found"}), 404

    try:
        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Income record deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete income: {str(e)}"}), 500
