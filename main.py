# main.py
# 핫딜 봇 메인 실행 스크립트

import sys
import time
import argparse
from datetime import datetime

from config import CHECK_INTERVAL_SECONDS, KEYWORD_FILTERS
from history import load_sent_deals, save_sent_deals
from scraper import fetch_latest_deals, fetch_direct_product_link
from link_helper import get_product_link
from copywriter import format_post
from notifier import send_deal_alert

# 윈도우 콘솔 UTF-8 인코딩 보장
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_pipeline(sent_deals: set) -> int:
    """새로운 핫딜을 탐색하고 전송하는 1회 주기 실행 함수"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] 핫딜 목록 확인 중...")
    
    deals = fetch_latest_deals()
    if not deals:
        print("  -> 수집된 핫딜이 없습니다.")
        return 0
        
    new_sent_count = 0
    
    # 최신순에서 거꾸로 순회하여 오래된 것부터 순차 전송
    for deal in reversed(deals):
        deal_id = deal['id']
        
        # 1. 중복 검사
        if deal_id in sent_deals:
            continue
            
        # 2. 키워드 필터 검사 (설정된 경우)
        if KEYWORD_FILTERS:
            matched = any(kw in deal['title'] for kw in KEYWORD_FILTERS)
            if not matched:
                sent_deals.add(deal_id)
                continue
                
        print(f"  [새 핫딜 발견] {deal['title']}")
        
        # 3. 원문 상세 쇼핑몰 주소 추출
        direct_url = fetch_direct_product_link(deal['ppom_url'])
        
        # 4. 최적의 제품 구매 링크 결정
        product_link = get_product_link(direct_url, deal['title'])
        
        # 5. 후킹글 + 가격비교 + 제품링크 3단 구조 메시지 포맷팅
        formatted_message = format_post(deal['title'], product_link)
        
        # 6. 텔레그램 알림 발송
        success = send_deal_alert(deal, formatted_message)
        if success:
            sent_deals.add(deal_id)
            new_sent_count += 1
            print(f"    -> 발송 완료! (ID: {deal_id})")
            time.sleep(2)  # 텔레그램 스팸 방지용 딜레이
        else:
            print(f"    -> [실패] 발송 실패 (ID: {deal_id})")
            
    if new_sent_count > 0:
        save_sent_deals(sent_deals)
        print(f"  -> 총 {new_sent_count}개의 새로운 핫딜 발송 완료.")
    else:
        print("  -> 새로운 핫딜이 없습니다.")
        
    return new_sent_count

def main():
    parser = argparse.ArgumentParser(description="실시간 핫딜 알림 봇")
    parser.add_argument("--once", action="store_true", help="1회만 실행하고 종료")
    parser.add_argument("--test", action="store_true", help="가장 최신 핫딜 1건 강제 전송 테스트")
    args = parser.parse_args()

    print("==================================================")
    print("🚀 실시간 핫딜 알림 봇 (deal-bot) 가동")
    print(f"⏱️ 확인 주기: {CHECK_INTERVAL_SECONDS}초")
    print("==================================================")
    
    sent_deals = load_sent_deals()
    print(f"기존 발송 완료된 핫딜 기록: {len(sent_deals)}건 로드됨\n")
    
    if args.test:
        print("[테스트 모드] 최신 핫딜 1건을 즉시 발송합니다.")
        deals = fetch_latest_deals()
        if deals:
            d = deals[0]
            direct = fetch_direct_product_link(d['ppom_url'])
            link = get_product_link(direct, d['title'])
            msg = format_post(d['title'], link)
            send_deal_alert(d, msg)
            print(f"  -> 테스트 발송 완료: {d['title']}")
        return

    if not sent_deals:
        print("[초기 설정] 첫 실행이므로 현재 글들을 기준점으로 등록합니다.")
        initial_deals = fetch_latest_deals()
        for d in initial_deals[1:]:  # 최신 1개 제외하고 모두 기발송 처리
            sent_deals.add(d['id'])
        save_sent_deals(sent_deals)

    if args.once:
        run_pipeline(sent_deals)
        return

    try:
        while True:
            run_pipeline(sent_deals)
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[알림] 사용자에 의해 봇이 안전하게 중단되었습니다.")
        save_sent_deals(sent_deals)

if __name__ == "__main__":
    main()
