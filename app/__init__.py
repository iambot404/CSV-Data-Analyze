import os
from flask import Flask
from flask_cors import CORS
from app.config import BASE_DIR, MAX_UPLOAD_SIZE_BYTES

def create_app():
    templates_dir = os.path.join(BASE_DIR, "templates")
    static_dir = os.path.join(BASE_DIR, "static")

    app = Flask(
        __name__,
        template_folder=templates_dir,
        static_folder=static_dir
    )
    
    # Configure limits
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_BYTES
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
