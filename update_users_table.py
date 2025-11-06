#!/usr/bin/env python3
"""
Users tablosuna eksik sütunları ekler
"""

import sqlite3
import os

def update_users_table():
    """Users tablosunu günceller"""
    # Olası veritabanı konumları
    possible_paths = [
        'instance/loki.db',
        'Pegasus-orjinal/server/instance/loki.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Hata: loki.db dosyası bulunamadı!")
        return False
    
    print(f"Veritabanı bulundu: {db_path}")
    
    try:
        # Veritabanına bağlan
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Users tablosu kontrol ediliyor...")
        
        # users tablosunun var olup olmadığını kontrol et
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Hata: users tablosu bulunamadı!")
            return False
        
        # Mevcut sütunları kontrol et
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        updates_made = False
        
        # last_login_time sütununu kontrol et
        if 'last_login_time' not in columns:
            print("last_login_time sütunu ekleniyor...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login_time DATETIME")
            updates_made = True
        else:
            print("last_login_time sütunu zaten mevcut.")
        
        # last_login_ip sütununu kontrol et
        if 'last_login_ip' not in columns:
            print("last_login_ip sütunu ekleniyor...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_login_ip VARCHAR(45)")
            updates_made = True
        else:
            print("last_login_ip sütunu zaten mevcut.")
        
        # Değişiklikleri kaydet
        if updates_made:
            conn.commit()
            print("Users tablosu başarıyla güncellendi!")
        else:
            print("Güncelleme gerekmiyor, tüm sütunlar zaten mevcut.")
        
        # Güncellenmiş şemayı göster
        print("\nGüncellenmiş users tablosu şeması:")
        cursor.execute("PRAGMA table_info(users)")
        for column in cursor.fetchall():
            print(f"  {column[1]} ({column[2]})")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return False
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        return False

if __name__ == "__main__":
    print("Users tablosu güncelleme scripti başlatılıyor...")
    print(f"Çalışma dizini: {os.getcwd()}")
    
    if update_users_table():
        print("\n✅ Users tablosu güncelleme başarılı!")
    else:
        print("\n❌ Users tablosu güncelleme başarısız!")
