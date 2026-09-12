# harvest_threads.py
# 스레드 벤치마킹 계정 시계열 데이터 수집기 (Time-series Harvester)

import sys
import os
import json
import hashlib
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

TARGET_ACCOUNTS = [
    'goodpicknote',   # 대표 핫딜/생필품/육아 큐레이터
    'jaeha.house',    # 블로그/제휴마케팅 바이럴 계정
    'bang100_e',      # 방구석 쿠파스/핫딜 꿀통 계정
]

TIMELINE_FILE = 'trend_timeline.jsonl'

def generate_post_id(account: str, text: str) -> str:
    """게시물 본문과 계정 기반 고유 해시 ID 생성 (중복 수집 방지)"""
    norm_text = text.strip()[:100]
    hash_val = hashlib.md5(f"{account}:{norm_text}".encode('utf-8')).hexdigest()[:12]
    return f"th_{account}_{hash_val}"

def load_existing_post_ids() -> set[str]:
    """기존 수집된 시계열 데이터에서 post_id 세트 로드"""
    if not os.path.exists(TIMELINE_FILE):
        return set()
    ids = set()
    with open(TIMELINE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    if 'post_id' in data:
                        ids.add(data['post_id'])
                except Exception:
                    continue
    return ids

def harvest_threads_hooks():
    existing_ids = load_existing_post_ids()
    print(f"📦 [시계열 스토리지] 기존 누적 데이터: {len(existing_ids)}건 감지됨")

    collected_records = []
    now_kst = datetime.now(timezone(timedelta(hours=9))).isoformat()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        
        for acc in TARGET_ACCOUNTS:
            url = f"https://www.threads.net/@{acc}"
            print(f"\n[수집 중] @{acc} 피드 탐색 중...")
            try:
                page.goto(url, timeout=25000)
                page.wait_for_timeout(3000)
                
                # 피드 스크롤 2회 수행하여 최신 글 및 반응 확보
                for _ in range(2):
                    page.mouse.wheel(0, 1500)
                    page.wait_for_timeout(1500)
                
                # 텍스트 스팬 추출
                spans = page.locator('span[dir="auto"]').all_text_contents()
                print(f"  -> 추출된 텍스트 조각 수: {len(spans)}")
                
                valid_posts = []
                for s in spans:
                    s_clean = s.strip()
                    # 유효 글 필터링 (너무 짧거나 인스타그램/스레드 기본 UI 버튼 제외)
                    if len(s_clean) > 20 and not any(skip in s_clean for skip in ['팔로워', 'Followers', 'Threads', '좋아요', '답글', '활동', '프로필 편집']):
                        valid_posts.append(s_clean)
                
                print(f"  -> 유효 후보 글: {len(valid_posts)}개")
                for vp in valid_posts[:5]:
                    lines = [ln.strip() for ln in vp.split('\n') if ln.strip()]
                    first_line = lines[0] if lines else vp[:50]
                    
                    # 단순 링크나 홍보용 URL 단독인 경우 제외
                    if first_line.startswith('http') or 'link.inpock' in first_line:
                        continue

                    post_id = generate_post_id(acc, vp)
                    if post_id in existing_ids:
                        continue  # 이미 수집된 글은 패스

                    record = {
                        'post_id': post_id,
                        'account': acc,
                        'collected_at': now_kst,
                        'first_line': first_line,
                        'content': vp,
                        'likes': 10,       # 기본 인게이지먼트 가중치
                        'replies': 2
                    }
                    collected_records.append(record)
                    existing_ids.add(post_id)
                    print(f"     ✨ [신규 수집] {first_line[:60]}")
                    
            except Exception as e:
                print(f"  [Error] @{acc} 수집 중 예외 발생: {e}")
                
        browser.close()

    # 시계열 파일(trend_timeline.jsonl)에 신규 데이터 Append
    if collected_records:
        with open(TIMELINE_FILE, 'a', encoding='utf-8') as f:
            for r in collected_records:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"\n✅ {len(collected_records)}건의 신규 트렌드 데이터가 {TIMELINE_FILE}에 시간순으로 누적되었습니다.")
    else:
        print(f"\nℹ️ 신규 수집된 새로운 포스트가 없습니다. (기존 데이터 유지)")

    return collected_records

if __name__ == '__main__':
    harvest_threads_hooks()
