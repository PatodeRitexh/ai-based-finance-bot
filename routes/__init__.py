from functools import wraps
from flask import session, jsonify, redirect, url_for, request


def login_required(f):
    """Decorator ensuring that an active user session exists."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            # Check if this is an API call or a page view
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required", "status": "unauthorized"}), 401
            return redirect(url_for("pages.login_view"))
        return f(*args, **kwargs)
    return decorated_function
