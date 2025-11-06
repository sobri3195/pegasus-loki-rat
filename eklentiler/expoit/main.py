import threading
import time
import logging
from queue import Queue
from config.config import ACCESS_TOKEN, THREAD_COUNT
from utils.request_handler import send_request
from utils.response_analyzer import analyze_response
from utils import report_generator

logging.basicConfig(
    filename='logs/bts_api_pentest.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

task_queue = Queue()

def load_payloads(file_path='payloads/payload_list.txt'):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def worker():
    while not task_queue.empty():
        bts_id = task_queue.get()
        response = send_request(bts_id, ACCESS_TOKEN)
        analyze_response(response, bts_id)
        task_queue.task_done()
        time.sleep(1)

def main():
    print("Starting BTS API pentest...")
    payloads = load_payloads()
    for payload in payloads:
        task_queue.put(payload)

    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("Pentest selesai. Membuat laporan summary...")
    report_generator.generate_report()
    print("Laporan summary selesai dibuat. Lihat folder reports/ untuk hasilnya.")

if __name__ == "__main__":
    main()
