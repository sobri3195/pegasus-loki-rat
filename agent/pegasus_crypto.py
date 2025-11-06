#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pegasus RAT şifreleme sistemi - Python adaptasyonu
Orijinal C# Aetos sınıfından uyarlanmıştır
"""

import os
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes
import struct

class PegasusAES:
    """
    Pegasus RAT'ın Aetos şifreleme sınıfının Python implementasyonu
    """
    
    def __init__(self, master_key):
        if not master_key:
            raise ValueError("Master key boş olamaz")
        
        # Orijinal C# kodundaki salt değeri
        self.salt = self._decode_string("ZOMKY_YHsYASDO^")
        
        # PBKDF2 ile anahtar türetme (C# Rfc2898DeriveBytes ile uyumlu)
        combined_key = PBKDF2(master_key, self.salt, 96, count=50000, hmac_hash_module=SHA256)
        
        # İlk 32 byte şifreleme anahtarı, sonraki 64 byte HMAC anahtarı
        self.encryption_key = combined_key[:32]
        self.auth_key = combined_key[32:96]
    
    def _decode_string(self, encoded_str):
        """
        Pegasus'un thebook fonksiyonunun Python karşılığı
        XOR ile '\n' karakteri kullanarak decode eder
        """
        result = []
        for char in encoded_str:
            decoded_char = chr(ord(char) ^ ord('\n'))
            result.append(decoded_char)
        return ''.join(result).encode('ascii')
    
    def encrypt(self, plaintext):
        """
        Veriyi şifreler ve HMAC ile doğrulama ekler
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # IV oluştur
        iv = get_random_bytes(16)
        
        # AES şifreleme
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        
        # PKCS7 padding
        pad_len = 16 - (len(plaintext) % 16)
        padded_data = plaintext + bytes([pad_len] * pad_len)
        
        # Şifrele
        ciphertext = cipher.encrypt(padded_data)
        
        # IV + şifrelenmiş veri
        encrypted_data = iv + ciphertext
        
        # HMAC hesapla
        hmac_obj = HMAC.new(self.auth_key, encrypted_data, SHA256)
        mac = hmac_obj.digest()
        
        # MAC + şifrelenmiş veri
        final_data = mac + encrypted_data
        
        return base64.b64encode(final_data).decode('ascii')
    
    def decrypt(self, ciphertext_b64):
        """
        Şifrelenmiş veriyi çözer ve HMAC doğrulaması yapar
        """
        try:
            # Base64 decode
            encrypted_data = base64.b64decode(ciphertext_b64)
            
            # MAC ve şifrelenmiş veriyi ayır
            mac = encrypted_data[:32]
            data_with_iv = encrypted_data[32:]
            
            # HMAC doğrulama
            hmac_obj = HMAC.new(self.auth_key, data_with_iv, SHA256)
            hmac_obj.verify(mac)
            
            # IV ve şifrelenmiş veriyi ayır
            iv = data_with_iv[:16]
            ciphertext = data_with_iv[16:]
            
            # AES çözme
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            padded_plaintext = cipher.decrypt(ciphertext)
            
            # PKCS7 padding kaldır
            pad_len = padded_plaintext[-1]
            plaintext = padded_plaintext[:-pad_len]
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            raise ValueError(f"Şifre çözme hatası: {str(e)}")

class PegasusConfig:
    """
    Pegasus RAT konfigürasyon yöneticisi
    """
    
    def __init__(self):
        # Pegasus'un orijinal şifrelenmiş ayarları
        self.encrypted_settings = {
            'ports': "IlqFRm9kpu0lTrg/HZB6/fLiF3Wuu18j0kBkcT2Rl+pM+wn35AXcj0qXP47/xO/BZFRWyhVTEzfMK/AN34PxTw==",
            'hosts': "ROLuQ2lQr2MYNN/JuLde6gNKNB3w4PUP3+pj9CnlWNhicenKAezZcskA5PPvdnMiYTA5qOW1QJCy+CkzOyAQkQ==",
            'version': "+jAuOIugiuitJMH21g7lTZoRoFfGEOzqxKPAJ3paPFFy3r3hzX/TJH3oWxtlCltqqyqsXI7hrC3YDZ8HHyQN8A==",
            'install': "DmdiBRp2gf2ivWf0bFWPeiThhElNzoKy3GWyBs27zbI56EkbGnSLa1ni7lsgooiBOQ5IC770VpzuClcUggQPQw==",
            'mutex': "pBLsHJ98Wvw/XlkLwORrIbirbmT8xwHnsJZ3DtYaPiwWeEJI21/x9B9GhgLzCQ1Kd074RDru+FZ3klXBy8baPqaKm8Q0lqAcDHIEpYbWlex9IK+ZzJsjP4hsX48hu+EsyV12ccUavXbIBla8PUNwtQ==",
            'group': "K7LwDz8urQaMKYCQoqD+nZgRHgigDY1I3xnNv1X4NKDX3qV71lrupA6TdcFaXZ/O4ag3LJlhhmQX7/69RYOc9A=="
        }
        
        # Orijinal master key (base64 encoded)
        self.master_key_b64 = "a2llNEFpNEwzRlBtbkcwM05kVGhUOXo5TkdPRmRjM2k="
        self.master_key = base64.b64decode(self.master_key_b64).decode('utf-8')
        
        # Şifreleme nesnesi
        self.crypto = PegasusAES(self.master_key)
        
        # Çözülmüş ayarlar
        self.settings = {}
        self._decrypt_settings()
    
    def _decrypt_settings(self):
        """
        Şifrelenmiş ayarları çözer
        """
        try:
            for key, encrypted_value in self.encrypted_settings.items():
                self.settings[key] = self.crypto.decrypt(encrypted_value)
        except Exception as e:
            print(f"Ayar çözme hatası: {e}")
            # Varsayılan değerler
            self.settings = {
                'ports': '8080,8443',
                'hosts': 'localhost,127.0.0.1',
                'version': '2.0',
                'install': 'true',
                'mutex': 'PegasusLokiMutex',
                'group': 'Default'
            }
    
    def get_setting(self, key, default=None):
        """
        Ayar değeri döndürür
        """
        return self.settings.get(key, default)
    
    def get_ports(self):
        """
        Port listesi döndürür
        """
        ports_str = self.get_setting('ports', '8080')
        return [int(p.strip()) for p in ports_str.split(',') if p.strip().isdigit()]
    
    def get_hosts(self):
        """
        Host listesi döndürür
        """
        hosts_str = self.get_setting('hosts', 'localhost')
        return [h.strip() for h in hosts_str.split(',') if h.strip()]

# Test fonksiyonu
if __name__ == "__main__":
    try:
        config = PegasusConfig()
        print("Pegasus Konfigürasyon Yüklendi:")
        print(f"Portlar: {config.get_ports()}")
        print(f"Hostlar: {config.get_hosts()}")
        print(f"Versiyon: {config.get_setting('version')}")
        print(f"Mutex: {config.get_setting('mutex')}")
        
        # Şifreleme testi
        crypto = PegasusAES(config.master_key)
        test_data = "Test verisi - Türkçe karakter testi: ğüşıöç"
        encrypted = crypto.encrypt(test_data)
        decrypted = crypto.decrypt(encrypted)
        
        print(f"\nŞifreleme Testi:")
        print(f"Orijinal: {test_data}")
        print(f"Şifrelenmiş: {encrypted}")
        print(f"Çözülmüş: {decrypted}")
        print(f"Başarılı: {test_data == decrypted}")
        
    except Exception as e:
        print(f"Hata: {e}")
