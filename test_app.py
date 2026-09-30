"""
System Verification Test Suite
Tests all authentication routes, API endpoints, CRUD operations, calculations,
and page views using Flask test client.
"""

from app import create_app
from models import db, User, Income, Expense, Budget, SavingsGoal


def run_tests():
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    print("========================================")
    print("RUNNING PERSONAL FINANCE BOT TEST SUITE")
    print("========================================")

    # 1. Test Static Pages
    pages = ["/", "/login", "/register", "/privacy", "/terms"]
    for path in pages:
        res = client.get(path)
        assert res.status_code == 200, f"Failed on {path}: {res.status_code}"
        print(f"[PASS] Page view {path} -> HTTP 200")

    # 2. Test Registration & Login
    with app.app_context():
        # Ensure fresh test user
        existing = User.query.filter_by(email="tester@example.com").first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

    reg_res = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": "tester@example.com", "password": "TestPass123!"},
    )
    assert reg_res.status_code == 201, f"Register failed: {reg_res.get_json()}"
    print("[PASS] User registration -> HTTP 201")

    login_res = client.post(
        "/api/auth/login",
        json={"email": "tester@example.com", "password": "TestPass123!"},
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.get_json()}"
    print("[PASS] User login -> HTTP 200")

    # 3. Test Income CRUD
    inc_res = client.post(
        "/api/income",
        json={"amount": 75000.0, "source": "Primary Salary", "date": "2026-09-01", "description": "September Salary"},
    )
    assert inc_res.status_code == 201, f"Add income failed: {inc_res.get_json()}"
    inc_id = inc_res.get_json()["item"]["id"]
    print(f"[PASS] Income created (ID: {inc_id}) -> HTTP 201")

    # 4. Test Expense CRUD
    exp_res = client.post(
        "/api/expenses",
        json={"amount": 18000.0, "category": "Rent", "date": "2026-09-02", "description": "Flat Rent"},
    )
    assert exp_res.status_code == 201, f"Add expense failed: {exp_res.get_json()}"
    exp_id = exp_res.get_json()["item"]["id"]
    print(f"[PASS] Expense recorded (ID: {exp_id}) -> HTTP 201")

    # 5. Test Budget CRUD
    bgt_res = client.post(
        "/api/budgets",
        json={"category": "Rent", "limit": 20000.0, "month": "2026-09"},
    )
    assert bgt_res.status_code in (200, 201), f"Set budget failed: {bgt_res.get_json()}"
    print("[PASS] Budget limit set -> HTTP 200/201")

    # 6. Test Savings Goals CRUD & Contribution
    goal_res = client.post(
        "/api/goals",
        json={"name": "Laptop Fund", "target_amount": 80000.0, "current_amount": 25000.0, "target_date": "2026-12-31"},
    )
    assert goal_res.status_code == 201, f"Add goal failed: {goal_res.get_json()}"
    goal_id = goal_res.get_json()["goal"]["id"]
    print(f"[PASS] Savings goal created (ID: {goal_id}) -> HTTP 201")

    dep_res = client.post(
        f"/api/goals/{goal_id}/deposit",
        json={"amount": 5000.0},
    )
    assert dep_res.status_code == 200, f"Deposit failed: {dep_res.get_json()}"
    assert dep_res.get_json()["goal"]["current_amount"] == 30000.0
    print("[PASS] Deposit added to savings goal -> HTTP 200")

    # 7. Test Dashboard Calculations
    dash_res = client.get("/api/dashboard?month=2026-09")
    assert dash_res.status_code == 200, f"Dashboard failed: {dash_res.get_json()}"
    data = dash_res.get_json()
    assert data["total_income"] == 75000.0
    assert data["total_expenses"] == 18000.0
    assert data["net_savings"] == 57000.0
    assert data["currency"] == "INR"
    assert data["currency_symbol"] == "₹"
    print(f"[PASS] Server-side calculations verified: Income={data['total_income']}, Expenses={data['total_expenses']}, Net Savings={data['net_savings']}")

    # 8. Test AI Advisor Endpoint
    ai_res = client.post(
        "/api/ai/analyze",
        json={"month": "2026-09"},
    )
    assert ai_res.status_code == 200, f"AI analyze failed: {ai_res.get_json()}"
    ai_data = ai_res.get_json()
    assert "monthly_financial_summary" in ai_data
    assert "spending_insights" in ai_data
    assert "disclaimer" in ai_data
    print(f"[PASS] AI Advisor endpoint returned valid financial analysis (source: {ai_data.get('source')})")

    # Cleanup test user
    with app.app_context():
        u = User.query.filter_by(email="tester@example.com").first()
        if u:
            db.session.delete(u)
            db.session.commit()
    print("[PASS] Test artifacts cleaned up successfully")

    print("========================================")
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("========================================")


if __name__ == "__main__":
    run_tests()
