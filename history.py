# history.py
# 이미 전송한 핫딜 번호를 저장하여 중복 발송을 방지하는 모듈

import json
import os
from config import MAX_HISTORY_ITEMS

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "sent_deals.json")

def load_sent_deals() -> set:
    """기존에 발송된 핫딜 ID 목록 로드"""
    if not os.path.exists(HISTORY_FILE):
        return set()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception as e:
        print(f"[Warning] 기록 파일 로드 실패: {e}")
        return set()

def save_sent_deals(sent_deals: set):
    """새로 발송된 핫딜 ID 목록 저장 (최신 MAX_HISTORY_ITEMS개만 유지)"""
    try:
        deals_list = list(sent_deals)[-MAX_HISTORY_ITEMS:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(deals_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Error] 기록 파일 저장 실패: {e}")
