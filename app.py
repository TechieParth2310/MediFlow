""" 
Doctor Appointment Management System
Industry-level Flask application with modular architecture
"""
from flask import Flask
from config import config
import os

# Import blueprints
from routes.main import main_bp
from routes.auth import auth_bp
from routes.doctor import doctor_bp
from routes.patient import patient_bp
from routes.admin import admin_bp


def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Store config object for blueprints to access
    app_config = config[config_name]

    # Inject config into blueprints
    main_bp.config = app_config
    auth_bp.config = app_config
    doctor_bp.config = app_config
    patient_bp.config = app_config
    admin_bp.config = app_config

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(admin_bp)

    # Context processor for global template variables
    @app.context_processor
    def inject_user():
        from flask import session
        return dict(
            logged_in='user_id' in session,
            user_role=session.get('role'),
            user_name=session.get('full_name'),
            user_email=session.get('email')
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        return render_template('errors/500.html'), 500

    # Create upload folder if it doesn't exist
    upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_folder, exist_ok=True)

    return app


# Create app instance
app = create_app(os.getenv('FLASK_ENV', 'development'))


# -----------------------------------------
# RUN APPLICATION
# -----------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
