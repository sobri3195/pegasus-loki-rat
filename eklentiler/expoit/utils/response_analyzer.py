import logging
import os
import requests

# MAIN_API_URL'ü config'ten almaya çalış, yoksa env veya default kullan
try:
    from config.config import MAIN_API_URL as CONFIG_MAIN_API_URL  # type: ignore
except Exception:
    CONFIG_MAIN_API_URL = None

MAIN_API_URL = CONFIG_MAIN_API_URL or os.environ.get('MAIN_API_URL') or 'http://127.0.0.1:5000/api'


def _send_event(status, bts_id, message, extra=None):
    try:
        requests.post(
            f"{MAIN_API_URL}/bts/event",
            json={
                "bts_id": bts_id,
                "status": status,
                "message": message,
                "extra": extra,
            },
            timeout=5,
        )
    except Exception:
        # API gönderimi opsiyonel; başarısız olsa bile aracı durdurma
        pass


def analyze_response(response, bts_id):
    if response is None:
        msg = f"No response for BTS ID {bts_id}"
        logging.error(msg)
        print(f"[ERROR] {msg}")
        _send_event("error", bts_id, msg)
        return

    if response.status_code == 200:
        try:
            data = response.json()
            if "location" in data:
                msg = f"BTS ID {bts_id} returned location data: {data['location']}"
                logging.info(f"[SUCCESS] {msg}")
                print(f"[SUCCESS] {msg}")
                _send_event("success", bts_id, msg, extra={"location": data.get("location")})
            else:
                msg = f"BTS ID {bts_id} response missing location field"
                logging.warning(f"[WARN] {msg}")
                print(f"[WARN] {msg}")
                _send_event("warn", bts_id, msg, extra={"keys": list(data.keys()) if isinstance(data, dict) else None})
        except ValueError:
            msg = f"BTS ID {bts_id} returned invalid JSON"
            logging.error(f"[ERROR] {msg}")
            print(f"[ERROR] {msg}")
            _send_event("error", bts_id, msg)
    else:
        msg = f"BTS ID {bts_id} returned status {response.status_code}"
        logging.warning(f"[FAIL] {msg}")
        print(f"[FAIL] {msg}")
        _send_event("fail", bts_id, msg, extra={"status_code": response.status_code, "text": response.text[:500] if hasattr(response, "text") else None})
