"""
Database Seed Script
Creates a demonstration user with realistic Indian financial records,
including multiple income streams, categorized expenses, monthly budgets,
and progress-tracked savings goals.
"""

from datetime import date, timedelta
from app import create_app
from models import db, User, Income, Expense, Budget, SavingsGoal


def seed_database():
    app = create_app()

    with app.app_context():
        print("Cleaning existing demo data...")
        demo_email = "demo@financebot.local"
        existing_user = User.query.filter_by(email=demo_email).first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print("Existing demo user removed.")

        print("Creating demo user...")
        user = User(
            name="Ritesh Sharma",
            email=demo_email,
        )
        user.set_password("DemoPass123!")
        db.session.add(user)
        db.session.commit()

        print(f"Created user: {user.email} (ID: {user.id})")

        today = date.today()
        current_month_str = today.strftime("%Y-%m")
        first_of_month = date(today.year, today.month, 1)

        # 1. Seed Income records
        incomes = [
            Income(
                user_id=user.id,
                amount=85000.0,
                source="Primary Salary",
                date=first_of_month,
                description="Monthly corporate salary credit (Tech firm)",
            ),
            Income(
                user_id=user.id,
                amount=18500.0,
                source="Freelance Consulting",
                date=first_of_month + timedelta(days=12),
                description="Backend API architecture and code review",
            ),
            Income(
                user_id=user.id,
                amount=4500.0,
                source="Mutual Fund Dividend",
                date=first_of_month + timedelta(days=18),
                description="Quarterly index fund distribution",
            ),
        ]

        # Previous month income for trend chart
        prev_month_date = first_of_month - timedelta(days=20)
        incomes.append(
            Income(
                user_id=user.id,
                amount=85000.0,
                source="Primary Salary",
                date=prev_month_date,
                description="Prior month salary",
            )
        )
        db.session.add_all(incomes)

        # 2. Seed Expense records for current month
        expenses = [
            Expense(
                user_id=user.id,
                amount=24000.0,
                category="Rent",
                date=first_of_month + timedelta(days=1),
                description="2BHK apartment rent in Bengaluru",
            ),
            Expense(
                user_id=user.id,
                amount=4200.0,
                category="Utilities",
                date=first_of_month + timedelta(days=3),
                description="Electricity, piped gas, and high-speed broadband",
            ),
            Expense(
                user_id=user.id,
                amount=9800.0,
                category="Food",
                date=first_of_month + timedelta(days=4),
                description="Monthly household groceries & provisions",
            ),
            Expense(
                user_id=user.id,
                amount=4150.0,
                category="Food",
                date=first_of_month + timedelta(days=10),
                description="Weekend dining and cafe visits",
            ),
            Expense(
                user_id=user.id,
                amount=5200.0,
                category="Transport",
                date=first_of_month + timedelta(days=6),
                description="Metro smart card recharge and commute fuel",
            ),
            Expense(
                user_id=user.id,
                amount=3600.0,
                category="Education",
                date=first_of_month + timedelta(days=8),
                description="Cloud engineering reference book and online course",
            ),
            Expense(
                user_id=user.id,
                amount=2100.0,
                category="Healthcare",
                date=first_of_month + timedelta(days=9),
                description="Routine dental checkup and prescription",
            ),
            Expense(
                user_id=user.id,
                amount=3850.0,
                category="Entertainment",
                date=first_of_month + timedelta(days=11),
                description="Streaming subscriptions and cinema tickets",
            ),
            Expense(
                user_id=user.id,
                amount=6400.0,
                category="Shopping",
                date=first_of_month + timedelta(days=13),
                description="Work attire and desk accessories",
            ),
            Expense(
                user_id=user.id,
                amount=1200.0,
                category="Other",
                date=first_of_month + timedelta(days=14),
                description="Courier and miscellaneous household supplies",
            ),
        ]

        # Prior month expense samples
        expenses.append(
            Expense(
                user_id=user.id,
                amount=24000.0,
                category="Rent",
                date=prev_month_date,
                description="Prior month apartment rent",
            )
        )
        expenses.append(
            Expense(
                user_id=user.id,
                amount=13500.0,
                category="Food",
                date=prev_month_date + timedelta(days=5),
                description="Prior month groceries and dining",
            )
        )

        db.session.add_all(expenses)

        # 3. Seed Monthly Budgets
        budgets = [
            Budget(user_id=user.id, month=current_month_str, category="Rent", limit=25000.0),
            Budget(user_id=user.id, month=current_month_str, category="Food", limit=16000.0),
            Budget(user_id=user.id, month=current_month_str, category="Transport", limit=6500.0),
            Budget(user_id=user.id, month=current_month_str, category="Utilities", limit=5000.0),
            Budget(user_id=user.id, month=current_month_str, category="Shopping", limit=6500.0),
            Budget(user_id=user.id, month=current_month_str, category="Entertainment", limit=3000.0),  # Will show exceeded!
            Budget(user_id=user.id, month=current_month_str, category="Education", limit=5000.0),
            Budget(user_id=user.id, month=current_month_str, category="Healthcare", limit=4000.0),
        ]
        db.session.add_all(budgets)

        # 4. Seed Savings Goals
        goals = [
            SavingsGoal(
                user_id=user.id,
                name="Emergency Reserve Fund",
                target_amount=180000.0,
                current_amount=120000.0,
                target_date=today + timedelta(days=180),
            ),
            SavingsGoal(
                user_id=user.id,
                name="M3 Workstation Laptop",
                target_amount=95000.0,
                current_amount=58000.0,
                target_date=today + timedelta(days=90),
            ),
            SavingsGoal(
                user_id=user.id,
                name="Professional Cloud Certifications",
                target_amount=40000.0,
                current_amount=24000.0,
                target_date=today + timedelta(days=120),
            ),
            SavingsGoal(
                user_id=user.id,
                name="Himalayan Trek & Travel",
                target_amount=35000.0,
                current_amount=12000.0,
                target_date=today + timedelta(days=150),
            ),
        ]
        db.session.add_all(goals)

        db.session.commit()
        print("Database successfully seeded with realistic Indian financial data!")
        print("Demo Credentials:")
        print(f"  Email:    {demo_email}")
        print("  Password: DemoPass123!")


if __name__ == "__main__":
    seed_database()
