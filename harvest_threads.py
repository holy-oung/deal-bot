import sys
import json
import re
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

TARGET_ACCOUNTS = ['goodpicknote', 'jaeha.house', 'bang100_e']

def harvest_threads_hooks():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        
        for acc in TARGET_ACCOUNTS:
            url = f"https://www.threads.net/@{acc}"
            print(f"\n[수집 중] @{acc} 페이지 접속...")
            try:
                page.goto(url, timeout=20000)
                page.wait_for_timeout(3000)
                
                # 피드 스크롤 1회 하여 글 추가 로드
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(2000)
                
                # 텍스트 노드 추출
                spans = page.locator('span[dir="auto"]').all_text_contents()
                print(f"  -> 추출된 텍스트 조각 수: {len(spans)}")
                
                # 유효한 본문/후킹 텍스트 필터링
                valid_posts = []
                for s in spans:
                    s_clean = s.strip()
                    # 너무 짧거나 시스템 텍스트 제외
                    if len(s_clean) > 25 and not any(skip in s_clean for skip in ['팔로워', 'Followers', 'Threads', '좋아요', '답글']):
                        valid_posts.append(s_clean)
                        
                print(f"  -> 유효한 후킹/본문 후보: {len(valid_posts)}개")
                for vp in valid_posts[:3]:
                    first_line = vp.split('\n')[0]
                    print(f"     🔥 {first_line[:80]}")
                    results.append({'account': acc, 'content': vp, 'first_line': first_line})
                    
            except Exception as e:
                print(f"  [Error] 수집 실패: {e}")
                
        browser.close()
    return results

if __name__ == '__main__':
    data = harvest_threads_hooks()
    with open('harvested_hooks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n총 {len(data)}개의 벤치마킹 데이터가 harvested_hooks.json에 저장되었습니다.")
