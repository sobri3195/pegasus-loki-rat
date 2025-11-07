#!/usr/bin/env python3
"""
Admin şifresini değiştiren script
"""

import sqlite3
import hashlib
import random
import string
import os

def hash_and_salt(password):
    """Şifre hashleme fonksiyonu"""
    password_hash = hashlib.sha256()
    salt = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
    password_hash.update((salt + password).encode('utf-8'))
    return password_hash.hexdigest(), salt

def change_admin_password(new_password):
    """Admin şifresini değiştirir"""
    db_path = 'instance/loki.db'

    if not os.path.exists(db_path):
        print(f"Hata: {db_path} dosyası bulunamadı!")
        return False

    try:
        # Veritabanına bağlan
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Admin kullanıcısını kontrol et
        cursor.execute("SELECT id, username FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()

        if not admin_user:
            print("Hata: Admin kullanıcısı bulunamadı!")
            return False

        print(f"Admin kullanıcısı bulundu: {admin_user[1]}")

        # Yeni şifreyi hashle
        password_hash, salt = hash_and_salt(new_password)
        print(f"Yeni şifre hashleniyor...")

        # Şifreyi güncelle
        cursor.execute("""
            UPDATE users
            SET password = ?, salt = ?
            WHERE username = 'admin'
        """, (password_hash, salt))

        # Değişiklikleri kaydet
        conn.commit()
        conn.close()

        print("✅ Admin şifresi başarıyla değiştirildi!")
        print(f"Yeni şifre: {new_password}")
        return True

    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return False
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        return False

if __name__ == "__main__":
    new_password = "Koraygs123."
    print("Admin şifre değiştirme scripti başlatılıyor...")
    print(f"Yeni şifre: {new_password}")

    if change_admin_password(new_password):
        print("\n✅ İşlem başarılı!")
    else:
        print("\n❌ İşlem başarısız!")
