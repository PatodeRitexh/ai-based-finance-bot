from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .income import Income
from .expense import Expense
from .budget import Budget
from .savings_goal import SavingsGoal

__all__ = ["db", "User", "Income", "Expense", "Budget", "SavingsGoal"]
