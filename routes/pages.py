from flask import Blueprint, render_template, session, redirect, url_for
from . import login_required

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """Landing page showcasing product features, architecture, and live demo access."""
    if "user_id" in session:
        return redirect(url_for("pages.dashboard_view"))
    return render_template("index.html")


@pages_bp.route("/login")
def login_view():
    """User login page."""
    if "user_id" in session:
        return redirect(url_for("pages.dashboard_view"))
    return render_template("login.html")


@pages_bp.route("/register")
def register_view():
    """User account registration page."""
    if "user_id" in session:
        return redirect(url_for("pages.dashboard_view"))
    return render_template("register.html")


@pages_bp.route("/dashboard")
@login_required
def dashboard_view():
    """Main application dashboard with tabbed financial views."""
    return render_template("dashboard.html", user_name=session.get("user_name", "User"))


@pages_bp.route("/privacy")
def privacy_view():
    """Privacy policy page."""
    return render_template("privacy.html")


@pages_bp.route("/terms")
def terms_view():
    """Terms and conditions page."""
    return render_template("terms.html")


@pages_bp.route("/logout")
def logout_view():
    """Logout redirect helper."""
    session.clear()
    return redirect(url_for("pages.login_view"))
