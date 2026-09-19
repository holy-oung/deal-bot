# history.py
# 이미 전송한 핫딜 번호 및 웜업 누적 확률 상태를 영속화하는 모듈

import json
import os
from datetime import datetime, timezone
from config import MAX_HISTORY_ITEMS

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "sent_deals.json")
WARMUP_STATE_FILE = os.path.join(os.path.dirname(__file__), "warmup_state.json")

BASE_WARMUP_PROBABILITY = 0.15  # 기본 발행 확률 15%

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

# =======================================================
# 웜업 모드 동적 확률 누적 상태 관리 (천장 Pity 시스템)
# =======================================================

def load_warmup_state() -> dict:
    """웜업 상태 파일 로드 (현재 확률, 연속 스킵 횟수, 마지막 발행 시각)"""
    default_state = {
        "current_probability": BASE_WARMUP_PROBABILITY,
        "consecutive_skips": 0,
        "last_posted_at": None
    }
    if not os.path.exists(WARMUP_STATE_FILE):
        return default_state
    try:
        with open(WARMUP_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return default_state
            return {
                "current_probability": float(data.get("current_probability", BASE_WARMUP_PROBABILITY)),
                "consecutive_skips": int(data.get("consecutive_skips", 0)),
                "last_posted_at": data.get("last_posted_at")
            }
    except Exception as e:
        print(f"[Warning] 웜업 상태 파일 로드 실패: {e}")
        return default_state

def save_warmup_state(state: dict):
    """웜업 상태 저장"""
    try:
        with open(WARMUP_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Error] 웜업 상태 파일 저장 실패: {e}")

def get_current_warmup_prob() -> float:
    """현재 회차에 적용될 웜업 발행 확률 조회"""
    state = load_warmup_state()
    return float(state.get("current_probability", BASE_WARMUP_PROBABILITY))

def record_warmup_result(posted: bool) -> tuple[float, float, int]:
    """
    발행 결과에 따른 확률 갱신:
    - 발행 성공 시: 기본 확률(15%)로 초기화, 연속 스킵 0으로 리셋
    - 발행 미실행(스킵) 시: 이전 확률의 절반(50%)을 가산하여 다음 확률 증가
      (예: 15% -> 22.5% -> 33.75% -> 50.6% -> 75.9% -> 100%)
    
    반환값: (적용된_확률, 갱신된_다음_확률, 연속_스킵_횟수)
    """
    state = load_warmup_state()
    curr_prob = float(state.get("current_probability", BASE_WARMUP_PROBABILITY))
    skips = int(state.get("consecutive_skips", 0))

    if posted:
        next_prob = BASE_WARMUP_PROBABILITY
        next_skips = 0
        state["last_posted_at"] = datetime.now(timezone.utc).isoformat()
    else:
        # 이전에 발행을 안 했으므로 이전 확률의 절반을 현재 확률에 더함
        add_amount = curr_prob * 0.5
        next_prob = min(1.0, round(curr_prob + add_amount, 4))
        next_skips = skips + 1

    state["current_probability"] = next_prob
    state["consecutive_skips"] = next_skips
    save_warmup_state(state)

    return curr_prob, next_prob, next_skips
