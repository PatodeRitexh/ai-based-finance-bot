from datetime import datetime, timezone, date
from . import db


class Income(db.Model):
    """User income record model."""

    __tablename__ = "incomes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Serialize income record for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": float(self.amount),
            "source": self.source,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
