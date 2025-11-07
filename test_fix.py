#!/usr/bin/env python3
"""
Veritabanı düzeltmesini test eder
"""

import sys
import os

# Pegasus-orjinal dizinini Python path'e ekle
sys.path.insert(0, 'Pegasus-orjinal')

try:
    from server.models import db, Agent
    from flask import Flask
    
    # Flask uygulaması oluştur
    app = Flask(__name__)
    
    # Doğru veritabanı yolunu bul
    current_dir = os.getcwd()
    possible_paths = [
        os.path.join(current_dir, 'instance', 'loki.db'),
        os.path.join(current_dir, 'Pegasus-orjinal', 'server', 'instance', 'loki.db')
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = f'sqlite:///{path}'
            break
    
    if not db_path:
        print("Veritabanı dosyası bulunamadı!")
        print("Aranan yollar:")
        for path in possible_paths:
            print(f"  - {path} (exists: {os.path.exists(path)})")
        sys.exit(1)
    
    print(f"Veritabanı yolu: {db_path}")
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Veritabanını başlat
    db.init_app(app)
    
    with app.app_context():
        # Agent'ları sorgula
        agents = Agent.query.order_by(Agent.last_online.desc()).all()
        print(f"✅ Test başarılı! {len(agents)} agent bulundu.")
        
        # Şemayı kontrol et
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns('agents')
        
        print("\nAgents tablosu sütunları:")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
        
        # last_seen ve status sütunlarının varlığını kontrol et
        column_names = [col['name'] for col in columns]
        if 'last_seen' in column_names and 'status' in column_names:
            print("\n✅ last_seen ve status sütunları başarıyla eklendi!")
        else:
            print("\n❌ Eksik sütunlar var!")
            
except Exception as e:
    print(f"❌ Test başarısız: {e}")
    import traceback
    traceback.print_exc()
