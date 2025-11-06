import requests
import time
import logging
from config.config import API_URL, MAX_RETRIES

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

def send_request(bts_id, token):
    params = {"bts_id": bts_id}
    headers = get_headers(token)
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(API_URL, headers=headers, params=params, timeout=10)
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 5))
                logging.warning(f"Rate limited. Waiting {wait_time} seconds before retrying.")
                time.sleep(wait_time)
                retries += 1
                continue
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception for BTS ID {bts_id}: {e}")
            retries += 1
            time.sleep(2)
    return None
