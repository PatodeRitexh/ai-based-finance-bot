from datetime import date, datetime
from calendar import monthrange
from sqlalchemy import func, extract
from models import db, Income, Expense, Budget, SavingsGoal


class FinanceService:
    """Service layer handling all financial calculations, validations, and data aggregation."""

    @staticmethod
    def get_current_month_str() -> str:
        """Return current month in YYYY-MM format."""
        today = date.today()
        return today.strftime("%Y-%m")

    @staticmethod
    def format_inr(amount: float) -> str:
        """Format a number into Indian Rupee style string (e.g. ₹1,50,000.00)."""
        if amount is None:
            return "₹0.00"
        
        is_negative = amount < 0
        amount = abs(amount)
        parts = f"{amount:.2f}".split(".")
        int_part = parts[0]
        dec_part = parts[1]

        if len(int_part) <= 3:
            formatted_int = int_part
        else:
            last3 = int_part[-3:]
            rest = int_part[:-3]
            chunks = []
            while len(rest) > 2:
                chunks.append(rest[-2:])
                rest = rest[:-2]
            if rest:
                chunks.append(rest)
            chunks.reverse()
            formatted_int = ",".join(chunks) + "," + last3

        prefix = "-₹" if is_negative else "₹"
        return f"{prefix}{formatted_int}.{dec_part}"

    @classmethod
    def get_user_dashboard_summary(cls, user_id: int, month_str: str = None) -> dict:
        """
        Aggregate full financial dashboard statistics for a given user and month.
        All calculations are executed server-side.
        """
        if not month_str:
            month_str = cls.get_current_month_str()

        try:
            year_int, month_int = map(int, month_str.split("-"))
        except (ValueError, AttributeError):
            today = date.today()
            year_int, month_int = today.year, today.month
            month_str = f"{year_int:04d}-{month_int:02d}"

        # 1. Total monthly income
        monthly_income_sum = (
            db.session.query(func.coalesce(func.sum(Income.amount), 0.0))
            .filter(
                Income.user_id == user_id,
                extract("year", Income.date) == year_int,
                extract("month", Income.date) == month_int,
            )
            .scalar()
        )
        total_income = float(monthly_income_sum)

        # 2. Total monthly expenses
        monthly_expense_sum = (
            db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year_int,
                extract("month", Expense.date) == month_int,
            )
            .scalar()
        )
        total_expenses = float(monthly_expense_sum)

        # 3. Current net savings & savings percentage
        net_savings = total_income - total_expenses
        savings_percentage = 0.0
        if total_income > 0:
            savings_percentage = round((net_savings / total_income) * 100.0, 2)

        # 4. Total Budget configured for this month
        budgets = (
            Budget.query.filter_by(user_id=user_id, month=month_str).all()
        )
        total_budget_limit = sum(float(b.limit) for b in budgets)

        # 5. Category-wise expense breakdown for the month
        category_spending_rows = (
            db.session.query(
                Expense.category,
                func.sum(Expense.amount).label("category_total"),
                func.count(Expense.id).label("tx_count"),
            )
            .filter(
                Expense.user_id == user_id,
                extract("year", Expense.date) == year_int,
                extract("month", Expense.date) == month_int,
            )
            .group_by(Expense.category)
            .all()
        )

        category_breakdown = {}
        for row in category_spending_rows:
            category_breakdown[row.category] = {
                "category": row.category,
                "amount": float(row.category_total),
                "transaction_count": int(row.tx_count),
                "percentage_of_expenses": (
                    round((float(row.category_total) / total_expenses) * 100.0, 2)
                    if total_expenses > 0
                    else 0.0
                ),
            }

        # 6. Budget vs Actual comparison
        budget_comparison = []
        budget_map = {b.category: float(b.limit) for b in budgets}
        all_categories = sorted(
            list(set(list(category_breakdown.keys()) + list(budget_map.keys())))
        )

        total_budget_spent = 0.0
        for cat in all_categories:
            spent = category_breakdown.get(cat, {}).get("amount", 0.0)
            limit = budget_map.get(cat, 0.0)
            remaining = limit - spent if limit > 0 else 0.0
            
            if limit > 0:
                pct_used = round((spent / limit) * 100.0, 2)
                total_budget_spent += spent
            else:
                pct_used = 0.0

            if limit == 0.0:
                status = "unbudgeted"
            elif pct_used >= 100.0:
                status = "exceeded"
            elif pct_used >= 80.0:
                status = "warning"
            else:
                status = "on_track"

            budget_comparison.append({
                "category": cat,
                "limit": limit,
                "spent": spent,
                "remaining": remaining,
                "percentage_used": pct_used,
                "status": status,
            })

        total_budget_remaining = max(0.0, total_budget_limit - total_expenses)

        # 7. Recent transactions (most recent 8 across income & expense)
        recent_incomes = (
            Income.query.filter_by(user_id=user_id)
            .order_by(Income.date.desc(), Income.id.desc())
            .limit(5)
            .all()
        )
        recent_expenses = (
            Expense.query.filter_by(user_id=user_id)
            .order_by(Expense.date.desc(), Expense.id.desc())
            .limit(5)
            .all()
        )

        recent_transactions = []
        for inc in recent_incomes:
            recent_transactions.append({
                "id": inc.id,
                "type": "income",
                "title": inc.source,
                "category": "Income",
                "amount": float(inc.amount),
                "date": inc.date.isoformat(),
                "description": inc.description or "",
            })
        for exp in recent_expenses:
            recent_transactions.append({
                "id": exp.id,
                "type": "expense",
                "title": exp.category,
                "category": exp.category,
                "amount": float(exp.amount),
                "date": exp.date.isoformat(),
                "description": exp.description or "",
            })

        # Sort combined transactions descending by date
        recent_transactions.sort(key=lambda x: x["date"], reverse=True)
        recent_transactions = recent_transactions[:8]

        # 8. Savings Goals Summary
        goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.target_date.asc()).all()
        goals_data = [g.to_dict() for g in goals]
        total_goal_target = sum(g["target_amount"] for g in goals_data)
        total_goal_saved = sum(g["current_amount"] for g in goals_data)
        overall_goal_pct = (
            round((total_goal_saved / total_goal_target) * 100.0, 2)
            if total_goal_target > 0
            else 0.0
        )

        # 9. Monthly Spending & Income Trend (Last 6 months)
        monthly_trend = cls._calculate_six_month_trend(user_id, year_int, month_int)

        return {
            "month": month_str,
            "currency": "INR",
            "currency_symbol": "₹",
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": net_savings,
            "savings_percentage": savings_percentage,
            "total_budget_limit": total_budget_limit,
            "total_budget_remaining": total_budget_remaining,
            "category_breakdown": category_breakdown,
            "budget_comparison": budget_comparison,
            "recent_transactions": recent_transactions,
            "savings_goals": {
                "items": goals_data,
                "total_target": total_goal_target,
                "total_saved": total_goal_saved,
                "overall_progress_percentage": overall_goal_pct,
            },
            "monthly_trend": monthly_trend,
        }

    @classmethod
    def _calculate_six_month_trend(cls, user_id: int, current_year: int, current_month: int) -> dict:
        """Generate monthly income vs expense time-series for the past 6 calendar months."""
        labels = []
        income_series = []
        expense_series = []

        # Generate (year, month) pairs for past 6 months ending with current
        target_months = []
        y = current_year
        m = current_month
        for _ in range(6):
            target_months.append((y, m))
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        target_months.reverse()

        for yr, mo in target_months:
            # Month label like 'May 2026'
            month_date = date(yr, mo, 1)
            month_label = month_date.strftime("%b %Y")
            labels.append(month_label)

            inc_val = (
                db.session.query(func.coalesce(func.sum(Income.amount), 0.0))
                .filter(
                    Income.user_id == user_id,
                    extract("year", Income.date) == yr,
                    extract("month", Income.date) == mo,
                )
                .scalar()
            )
            exp_val = (
                db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))
                .filter(
                    Expense.user_id == user_id,
                    extract("year", Expense.date) == yr,
                    extract("month", Expense.date) == mo,
                )
                .scalar()
            )

            income_series.append(float(inc_val))
            expense_series.append(float(exp_val))

        return {
            "labels": labels,
            "income": income_series,
            "expenses": expense_series,
        }
