from datetime import datetime, timezone
from . import db


class Budget(db.Model):
    """Monthly category-level budget limit model."""

    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    month = db.Column(db.String(7), nullable=False)  # Format: "YYYY-MM"
    category = db.Column(db.String(50), nullable=False)
    limit = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("user_id", "month", "category", name="uq_user_month_category"),
    )

    def to_dict(self):
        """Serialize budget record for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "month": self.month,
            "category": self.category,
            "limit": float(self.limit),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
