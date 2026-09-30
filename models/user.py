from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    """User account model for authentication and data isolation."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships - strictly scoped to user
    incomes = db.relationship("Income", backref="user", cascade="all, delete-orphan", lazy=True)
    expenses = db.relationship("Expense", backref="user", cascade="all, delete-orphan", lazy=True)
    budgets = db.relationship("Budget", backref="user", cascade="all, delete-orphan", lazy=True)
    savings_goals = db.relationship("SavingsGoal", backref="user", cascade="all, delete-orphan", lazy=True)

    def set_password(self, password: str):
        """Hash and store the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify the user password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Return serialized user data (excluding password)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
