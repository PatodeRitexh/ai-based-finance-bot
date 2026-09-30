from datetime import datetime, timezone, date
from . import db


class SavingsGoal(db.Model):
    """User savings target model."""

    __tablename__ = "savings_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, nullable=False, default=0.0)
    target_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage capped at 100%."""
        if self.target_amount <= 0:
            return 0.0
        pct = (self.current_amount / self.target_amount) * 100.0
        return round(pct, 2)

    def to_dict(self):
        """Serialize savings goal for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "target_amount": float(self.target_amount),
            "current_amount": float(self.current_amount),
            "remaining_amount": max(0.0, float(self.target_amount) - float(self.current_amount)),
            "progress_percentage": self.progress_percentage,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
