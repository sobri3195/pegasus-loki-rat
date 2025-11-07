#!/usr/bin/env python3
"""
Veritabanı şemasını güncelleyerek eksik sütunları ekler
"""

import sqlite3
import os
from datetime import datetime

def check_column_exists(cursor, table_name, column_name):
    """Sütunun var olup olmadığını kontrol eder"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

def update_database_schema():
    """Veritabanı şemasını günceller"""
    # Olası veritabanı konumları
    possible_paths = [
        'loki.db',
        'instance/loki.db',
        'Pegasus-orjinal/server/instance/loki.db'
    ]
    
    # Tüm veritabanlarını güncelle
    updated_dbs = []
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"\nVeritabanı bulundu: {path}")
            if update_single_database(path):
                updated_dbs.append(path)
    
    if not updated_dbs:
        print("Hata: Hiç veritabanı bulunamadı!")
        print("Aranan konumlar:")
        for path in possible_paths:
            print(f"  - {path}")
        return False
    
    print(f"\nToplam {len(updated_dbs)} veritabanı güncellendi:")
    for db in updated_dbs:
        print(f"  ✅ {db}")
    
    return True

def update_single_database(db_path):
    """Tek bir veritabanını günceller"""
    
    try:
        # Veritabanına bağlan
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Mevcut veritabanı şeması kontrol ediliyor...")
        
        # agents tablosunun var olup olmadığını kontrol et
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agents'")
        if not cursor.fetchone():
            print("Hata: agents tablosu bulunamadı!")
            return False
        
        # Eksik sütunları kontrol et ve ekle
        updates_made = False
        
        # last_seen sütununu kontrol et
        if not check_column_exists(cursor, 'agents', 'last_seen'):
            print("last_seen sütunu ekleniyor...")
            cursor.execute("ALTER TABLE agents ADD COLUMN last_seen DATETIME")
            updates_made = True
        else:
            print("last_seen sütunu zaten mevcut.")
        
        # status sütununu kontrol et
        if not check_column_exists(cursor, 'agents', 'status'):
            print("status sütunu ekleniyor...")
            cursor.execute("ALTER TABLE agents ADD COLUMN status VARCHAR(20) DEFAULT 'offline'")
            updates_made = True
        else:
            print("status sütunu zaten mevcut.")
        
        # commands tablosunu kontrol et ve eksik sütunları ekle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commands'")
        if cursor.fetchone():
            print("\ncommands tablosu kontrol ediliyor...")
            
            # executed sütununu kontrol et
            if not check_column_exists(cursor, 'commands', 'executed'):
                print("commands.executed sütunu ekleniyor...")
                cursor.execute("ALTER TABLE commands ADD COLUMN executed BOOLEAN DEFAULT 0")
                updates_made = True
            else:
                print("commands.executed sütunu zaten mevcut.")
            
            # completed_at sütununu kontrol et
            if not check_column_exists(cursor, 'commands', 'completed_at'):
                print("commands.completed_at sütunu ekleniyor...")
                cursor.execute("ALTER TABLE commands ADD COLUMN completed_at DATETIME")
                updates_made = True
            else:
                print("commands.completed_at sütunu zaten mevcut.")
            
            # output sütununu kontrol et
            if not check_column_exists(cursor, 'commands', 'output'):
                print("commands.output sütunu ekleniyor...")
                cursor.execute("ALTER TABLE commands ADD COLUMN output TEXT")
                updates_made = True
            else:
                print("commands.output sütunu zaten mevcut.")
            
            # error sütununu kontrol et
            if not check_column_exists(cursor, 'commands', 'error'):
                print("commands.error sütunu ekleniyor...")
                cursor.execute("ALTER TABLE commands ADD COLUMN error TEXT")
                updates_made = True
            else:
                print("commands.error sütunu zaten mevcut.")
            
            # return_code sütununu kontrol et
            if not check_column_exists(cursor, 'commands', 'return_code'):
                print("commands.return_code sütunu ekleniyor...")
                cursor.execute("ALTER TABLE commands ADD COLUMN return_code INTEGER")
                updates_made = True
            else:
                print("commands.return_code sütunu zaten mevcut.")
        else:
            print("commands tablosu bulunamadı.")
        
        # Değişiklikleri kaydet
        if updates_made:
            conn.commit()
            print("Veritabanı şeması başarıyla güncellendi!")
            
            # Mevcut agent'ların status değerlerini güncelle
            cursor.execute("UPDATE agents SET status = 'offline' WHERE status IS NULL")
            conn.commit()
            print("Mevcut agent'ların status değerleri güncellendi.")
        else:
            print("Güncelleme gerekmiyor, tüm sütunlar zaten mevcut.")
        
        # Güncellenmiş şemayı göster
        print("\nGüncellenmiş agents tablosu şeması:")
        cursor.execute("PRAGMA table_info(agents)")
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
    print("Veritabanı şema güncelleme scripti başlatılıyor...")
    print(f"Çalışma dizini: {os.getcwd()}")
    
    if update_database_schema():
        print("\n✅ Şema güncelleme başarılı!")
        print("Artık uygulamayı çalıştırabilirsiniz.")
    else:
        print("\n❌ Şema güncelleme başarısız!")
