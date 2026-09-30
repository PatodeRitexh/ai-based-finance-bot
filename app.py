import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS

from config import Config
from models import db
from routes.pages import pages_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.income import income_bp
from routes.expenses import expenses_bp
from routes.budgets import budgets_bp
from routes.goals import goals_bp
from routes.ai import ai_bp


def create_app(config_class=Config) -> Flask:
    """Application factory initializing extensions, blueprints, and database tables."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for local REST clients if needed
    CORS(app, supports_credentials=True)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(ai_bp)

    # Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return render_template("base.html", not_found=True), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({"error": "Internal server error occurred", "status": 500}), 500

    # Ensure tables exist
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1").lower() in ("1", "true")
    print(f"Personal Finance Advisor Bot starting on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=debug)
