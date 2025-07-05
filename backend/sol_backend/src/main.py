import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db, Admin
from src.routes.auth import auth_bp
from src.routes.wallet import wallet_bp
from src.routes.admin import admin_bp
from src.routes.webhooks import webhooks_bp
from src.routes.privy import privy_bp
from src.routes.xendit import xendit_bp
from src.routes.doku import doku_bp
import bcrypt

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = 'sol-mvp-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'sol-mvp-jwt-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # For development, disable token expiration

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize JWT
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(wallet_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(webhooks_bp, url_prefix='/api')
app.register_blueprint(privy_bp, url_prefix='/api')
app.register_blueprint(xendit_bp, url_prefix='/api')
app.register_blueprint(doku_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_default_admin():
    """Create a default admin user if none exists"""
    with app.app_context():
        if not Admin.query.first():
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = Admin(
                username='admin',
                password_hash=password_hash,
                email='admin@sol.com'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: username=admin, password=admin123")

# Initialize database and create tables
with app.app_context():
    db.create_all()
    create_default_admin()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Sol MVP API Server is running", 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return {
        'status': 'healthy',
        'service': 'Sol MVP API',
        'version': '1.0.0'
    }, 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

