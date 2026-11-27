"""Application factory for ClinicCare."""

from flask import Flask, render_template
from app.extensions import db
from app.patterns.singleton import AppConfig, DatabaseSessionManager


def create_app(test_config=None):
    """Create, configure and return Flask application instance."""
    flask_app = Flask(__name__, instance_relative_config=True)

    config = AppConfig()
    flask_app.config.from_mapping(
        SECRET_KEY=config.SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=config.SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=config.SQLALCHEMY_TRACK_MODIFICATIONS,
    )

    if test_config:
        flask_app.config.update(test_config)

    # Initialize extensions
    db.init_app(flask_app)
    import app.models  # noqa: F401
    session_manager = DatabaseSessionManager()
    session_manager.set_db(db)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.patient import patient_bp
    from app.routes.public import public_bp
    from app.routes.doctor import doctor_bp
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(patient_bp)
    flask_app.register_blueprint(public_bp)
    flask_app.register_blueprint(doctor_bp)

    @flask_app.route("/admin/dashboard")
    def admin_dashboard():
        return "Admin Dashboard"

    # Error handlers
    @flask_app.errorhandler(403)
    def forbidden_error(e):
        return render_template("errors/403.html"), 403

    @flask_app.errorhandler(404)
    def not_found_error(e):
        return render_template("errors/404.html"), 404

    @flask_app.errorhandler(500)
    def internal_error(e):
        return "Internal Server Error", 500

    return flask_app
