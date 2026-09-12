# threads_insights.py
# Meta Threads Graph API 계정 인사이트 수집 및 고성과 후킹 피드백 강화 모듈

import os
import sys
import json
import time
import requests
from datetime import datetime, timezone, timedelta

from config import THREADS_ACCESS_TOKEN, THREADS_USER_ID, ENABLE_THREADS_POSTING
from copywriter import clean_title_for_display, classify_deal_category

sys.stdout.reconfigure(encoding='utf-8')

GRAPH_API_BASE = "https://graph.threads.net/v1.0"
TIMELINE_FILE = 'trend_timeline.jsonl'

def is_threads_active() -> bool:
    return bool(THREADS_ACCESS_TOKEN and THREADS_USER_ID)

def fetch_my_recent_threads(limit: int = 25) -> list[dict]:
    """내 스레드 계정의 최근 발행 게시물 목록 조회"""
    if not is_threads_active():
        return []

    url = f"{GRAPH_API_BASE}/{THREADS_USER_ID}/threads"
    params = {
        "fields": "id,text,timestamp,media_type,permalink",
        "access_token": THREADS_ACCESS_TOKEN,
        "limit": limit
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", [])
        print(f"[Threads Insights Error] 게시글 목록 조회 실패: {res.text}")
    except Exception as e:
        print(f"[Threads Insights Exception] {e}")
    return []

def fetch_thread_insights(media_id: str) -> dict:
    """단일 스레드 게시물의 조회수(views), 좋아요(likes), 답글(replies) 인사이트 조회"""
    metrics = {"views": 0, "likes": 0, "replies": 0, "reposts": 0}
    if not is_threads_active():
        return metrics

    url = f"{GRAPH_API_BASE}/{media_id}/insights"
    params = {
        "metric": "views,likes,replies,reposts,quotes",
        "access_token": THREADS_ACCESS_TOKEN
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json().get("data", [])
            for item in data:
                name = item.get("name")
                vals = item.get("values", [])
                val = vals[0].get("value", 0) if vals else 0
                if name in metrics:
                    metrics[name] = val
        else:
            # 갓 발행된 포스트는 insights 집계 전일 수 있음
            pass
    except Exception as e:
        print(f"[Threads Insights Warning] {media_id} 인사이트 조회 예외: {e}")
    return metrics

def get_top_performing_threads(top_k: int = 3, hours_window: int = 48) -> list[dict]:
    """
    최근 hours_window 시간 내 발행된 글 중 조회수(views) 기준 Top K 게시글 추출
    """
    threads = fetch_my_recent_threads(limit=30)
    if not threads:
        return []

    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(hours=hours_window)

    analyzed_threads = []

    for th in threads:
        text = th.get("text", "")
        ts_str = th.get("timestamp", "")
        th_id = th.get("id")
        permalink = th.get("permalink", f"https://www.threads.net/t/{th_id}")

        # 첫 번째 댓글(구매 링크)은 제외 (본문 포스트만 선별)
        if text.startswith("👉 실시간 최저가") or "※ 파트너스 활동" in text:
            continue

        # 시간 파싱
        try:
            # Format: 2026-09-12T05:11:54+0000
            ts_clean = ts_str.replace("+0000", "+00:00")
            dt = datetime.fromisoformat(ts_clean)
            if dt < cutoff:
                continue
        except Exception:
            pass

        # 메트릭 조회
        insights = fetch_thread_insights(th_id)
        time.sleep(0.3)  # API Rate limit 방지 딜레이

        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        hook = lines[0] if lines else ""
        product_line = lines[1] if len(lines) > 1 else ""

        category = classify_deal_category(text)

        analyzed_threads.append({
            "id": th_id,
            "hook": hook,
            "product_line": product_line,
            "category": category,
            "views": insights.get("views", 0),
            "likes": insights.get("likes", 0),
            "replies": insights.get("replies", 0),
            "permalink": permalink,
            "timestamp": ts_str,
            "raw_text": text
        })

    # 조회수(views) 내림차순, 동일하면 좋아요(likes) 순 정렬
    analyzed_threads.sort(key=lambda x: (x["views"], x["likes"]), reverse=True)
    return analyzed_threads[:top_k]

def reinforce_high_performing_posts(top_posts: list[dict]):
    """
    내 계정에서 조회수가 터진 상위 포스트들을 시계열 DB(trend_timeline.jsonl)에 
    고가중치 자체 검증 데이터(Feedback Loop)로 주입하여 다음 날 생성 시 우선 채택되도록 강화
    """
    if not top_posts:
        return

    existing_ids = set()
    if os.path.exists(TIMELINE_FILE):
        with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        d = json.loads(line)
                        if "post_id" in d:
                            existing_ids.add(d["post_id"])
                    except Exception:
                        pass

    now_kst = datetime.now(timezone(timedelta(hours=9))).isoformat()
    new_records = []

    for post in top_posts:
        my_post_id = f"th_my_{post['id']}"
        # 이미 피드백된 포스트라도 조회수/좋아요가 대폭 갱신되었을 수 있으므로 업데이트 형식으로 주입
        record = {
            "post_id": my_post_id,
            "account": "my_threads_top",
            "collected_at": now_kst,
            "first_line": post["hook"],
            "content": post["raw_text"],
            "likes": max(15, post["views"] // 2 + post["likes"] * 3),  # 조회수를 인게이지먼트로 반영
            "replies": max(3, post["replies"] * 2),
            "is_self_feedback": True
        }
        new_records.append(record)

    if new_records:
        with open(TIMELINE_FILE, "a", encoding="utf-8") as f:
            for r in new_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"🔄 [피드백 루프] 내 계정 Top {len(new_records)}개 포스트가 시계열 DB에 강화 데이터로 자동 주입되었습니다.")

        # 트렌드 분석 엔진 즉시 재실행하여 dynamic_hook_pool.json에 반영
        try:
            from trend_analyzer import run_trend_analysis
            run_trend_analysis()
            print("🚀 [강화 학습 완료] 잘 터진 후킹 템플릿이 동적 풀 최상위 가중치로 승격되었습니다.")
        except Exception as e:
            print(f"[Warning] 재학습 호출 실패: {e}")

if __name__ == "__main__":
    print("🔍 [Threads] 최근 내 계정 게시물 인사이트 분석 중...")
    top_3 = get_top_performing_threads(top_k=3, hours_window=72)
    for idx, p in enumerate(top_3, 1):
        print(f"\n[{idx}위] 조회수: {p['views']}회 | ❤️ {p['likes']} | 💬 {p['replies']}")
        print(f"  카테고리: {p['category']}")
        print(f"  후킹: {p['hook']}")
        print(f"  상품: {p['product_line']}")
        print(f"  링크: {p['permalink']}")

    if top_3:
        reinforce_high_performing_posts(top_3)
