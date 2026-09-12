# main.py
# 핫딜 봇 메인 실행 스크립트

import os
import sys
import time
import argparse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta, timezone

from config import CHECK_INTERVAL_SECONDS, KEYWORD_FILTERS
from history import load_sent_deals, save_sent_deals
from scraper import fetch_latest_deals, fetch_direct_product_link, fetch_deal_details, is_monetizable_deal
from link_helper import get_product_link
from copywriter import format_post, format_threads_post
from notifier import send_deal_alert
from threads_poster import post_to_threads, is_threads_configured, validate_threads_credentials

# Render Web Service 무료 티어 유지를 위한 경량 헬스체크 HTTP 핸들러
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"deal-bot is healthy and running!")
    def log_message(self, format, *args):
        pass  # 헬스체크 핑 콘솔 로그 억제

def start_health_check_server():
    port = int(os.getenv("PORT", "8000"))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        print(f"🌐 [클라우드 헬스체크] 포트 {port}에서 정상 대기 중...")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ [헬스체크 서버 알림] {e}")

# 스레드 알고리즘 최적화 안전장치 (도배 방지 및 심야 휴식)
MIN_POST_COOLDOWN_SECONDS = 600  # 최소 10분(600초) 간격 포스팅
NIGHT_SLEEP_START_HOUR = 1       # 새벽 1시(KST)부터
NIGHT_SLEEP_END_HOUR = 7         # 아침 7시(KST)까지

def is_night_sleep_time() -> bool:
    """한국 시간(KST) 기준 심야 취침 시간대(01:00 ~ 07:00) 여부 확인"""
    kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
    return NIGHT_SLEEP_START_HOUR <= kst_now.hour < NIGHT_SLEEP_END_HOUR

# 윈도우 콘솔 UTF-8 인코딩 보장
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_pipeline(sent_deals: set, last_post_time: float = 0.0) -> tuple[int, float]:
    """새로운 핫딜을 탐색하고 전송하는 1회 주기 실행 함수"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] 핫딜 목록 확인 중...")
    
    if is_night_sleep_time():
        kst_now = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%H:%M")
        print(f"  🌙 [심야 취침 모드 ({kst_now} KST)] 유저 반응 골든타임 사장 방지를 위해 대기합니다.")
        return 0, last_post_time
        
    deals = fetch_latest_deals()
    if not deals:
        print("  -> 수집된 핫딜이 없습니다.")
        return 0, last_post_time
        
    new_sent_count = 0
    
    # 최신순에서 거꾸로 순회하여 오래된 것부터 순차 전송
    for deal in reversed(deals):
        deal_id = deal['id']
        
        # 1. 중복 검사
        if deal_id in sent_deals:
            continue
            
        # 2. 비수익성(알뜰폰, 상품권, 네이버페이 등) 딜 원천 필터링
        can_monetize, reason = is_monetizable_deal(deal['title'], deal['ppom_url'])
        if not can_monetize:
            print(f"  [수익화 불가 제외] {deal['title']} -> {reason}")
            sent_deals.add(deal_id)
            continue

        # 3. 키워드 필터 검사 (설정된 경우)
        if KEYWORD_FILTERS:
            matched = any(kw in deal['title'] for kw in KEYWORD_FILTERS)
            if not matched:
                sent_deals.add(deal_id)
                continue
                
        print(f"  [새 핫딜 발견] {deal['title']}")
        
        # 4. 듀얼 트랙(Track 1: 원문 맥락 & Track 2: 1차 출처) 정보 수집 및 고해상도 이미지 선별
        details = fetch_deal_details(deal['ppom_url'])
        direct_url = details['direct_url']
        high_res_image = details['high_res_image']
        context_text = details['context_text']
        print(f"    [{details['image_reason']}]")
        
        # 상세 주소 기준 2차 비수익 도메인(알뜰폰 등) 검사
        can_monetize, reason = is_monetizable_deal(deal['title'], direct_url)
        if not can_monetize:
            print(f"  [수익화 불가 제외 (상세)] {deal['title']} -> {reason}")
            sent_deals.add(deal_id)
            continue
        
        # 도배 방지 쿨타임 검사 (마지막 스레드 발행 후 최소 10분 간격 유지)
        elapsed = time.time() - last_post_time
        if last_post_time > 0 and elapsed < MIN_POST_COOLDOWN_SECONDS:
            remain = int(MIN_POST_COOLDOWN_SECONDS - elapsed)
            print(f"  ⏳ [도배 방지 쿨타임] 마지막 발행 후 {int(elapsed)}초 경과. 스레드 계정 보호를 위해 {remain}초 후 다음 턴에 발행합니다.")
            break

        # 5. 최적의 제품 구매 링크 결정 (100% 쿠팡 파트너스 링크 반환)
        product_link = get_product_link(direct_url, deal['title'])
        
        # 6. 후킹글 + 가격비교 + 제품링크 3단 구조 메시지 포맷팅
        formatted_message = format_post(deal['title'], product_link)
        
        # 7. 텔레그램 알림 발송
        success = send_deal_alert(deal, formatted_message)
        
        # 8. 스레드(Threads) 2단 분리 자동 포스팅 (정보 해상도 강화 + 고해상도 이미지 또는 클린 텍스트 모드)
        root_text, reply_text = format_threads_post(deal['title'], product_link, context_text=context_text)
        threads_res = post_to_threads(root_text, reply_text, image_url=high_res_image)
        
        if success or threads_res.get('success'):
            sent_deals.add(deal_id)
            new_sent_count += 1
            last_post_time = time.time()
            print(f"    -> 발송 완료! (ID: {deal_id})")
            time.sleep(2)  # 텔레그램 스팸 방지용 딜레이
        else:
            print(f"    -> [실패] 발송 실패 (ID: {deal_id})")
            
    if new_sent_count > 0:
        save_sent_deals(sent_deals)
        print(f"  -> 총 {new_sent_count}개의 새로운 핫딜 발송 완료.")
    else:
        print("  -> 새로운 핫딜이 없습니다.")
        
    return new_sent_count, last_post_time

def main():
    parser = argparse.ArgumentParser(description="실시간 핫딜 알림 봇")
    parser.add_argument("--once", action="store_true", help="1회만 실행하고 종료")
    parser.add_argument("--test", action="store_true", help="가장 최신 핫딜 1건 강제 전송 테스트 (텔레그램 + 스레드)")
    parser.add_argument("--threads-test", action="store_true", help="최신 핫딜 1건 스레드(Threads) 포스팅만 단독 테스트")
    parser.add_argument("--verify-threads", action="store_true", help="Threads API 토큰 및 계정 자격증명 유효성 검사")
    args = parser.parse_args()

    # 1. 스레드 토큰 검증 옵션
    if args.verify_threads:
        print("🔍 [Threads] 계정 자격증명 검증 중...")
        res = validate_threads_credentials()
        if res.get("valid"):
            print(f"  ✅ 인증 성공! 유저네임: @{res.get('username')} (ID: {res.get('userId')})")
        else:
            print(f"  ❌ 인증 실패: {res.get('error')}")
        return

    # 2. 스레드 단독 테스트 옵션
    if args.threads_test:
        print("🧵 [테스트 모드] 최신 핫딜 중 수익화 가능한 1건으로 스레드 포스팅을 테스트합니다.")
        deals = fetch_latest_deals()
        target_deal = None
        for d in deals:
            can_monetize, _ = is_monetizable_deal(d['title'], d['ppom_url'])
            if can_monetize:
                target_deal = d
                break
        if target_deal:
            details = fetch_deal_details(target_deal['ppom_url'])
            print(f"  [{details['image_reason']}]")
            direct = details['direct_url']
            link = get_product_link(direct, target_deal['title'])
            root_text, reply_text = format_threads_post(target_deal['title'], link, context_text=details['context_text'])
            post_to_threads(root_text, reply_text, image_url=details['high_res_image'])
        else:
            print("  -> 현재 수집된 핫딜 중 수익화 가능한 핫딜이 없습니다.")
        return

    print("==================================================")
    print("🚀 실시간 핫딜 알림 봇 (deal-bot) 가동")
    print(f"⏱️ 확인 주기: {CHECK_INTERVAL_SECONDS}초")
    print("==================================================")
    
    sent_deals = load_sent_deals()
    print(f"기존 발송 완료된 핫딜 기록: {len(sent_deals)}건 로드됨\n")
    
    if args.test:
        print("[테스트 모드] 최신 핫딜 1건을 즉시 발송합니다 (텔레그램 + 스레드).")
        deals = fetch_latest_deals()
        target_deal = None
        for d in deals:
            can_monetize, _ = is_monetizable_deal(d['title'], d['ppom_url'])
            if can_monetize:
                target_deal = d
                break
        if target_deal:
            details = fetch_deal_details(target_deal['ppom_url'])
            print(f"  [{details['image_reason']}]")
            direct = details['direct_url']
            link = get_product_link(direct, target_deal['title'])
            msg = format_post(target_deal['title'], link)
            send_deal_alert(target_deal, msg)
            root_text, reply_text = format_threads_post(target_deal['title'], link, context_text=details['context_text'])
            post_to_threads(root_text, reply_text, image_url=details['high_res_image'])
            print(f"  -> 테스트 발송 완료: {target_deal['title']}")
        else:
            print("  -> 현재 수집된 핫딜 중 수익화 가능한 핫딜이 없습니다.")
        return

    if not sent_deals:
        print("[초기 설정] 첫 실행이므로 현재 글들을 기준점으로 등록합니다.")
        initial_deals = fetch_latest_deals()
        for d in initial_deals[1:]:  # 최신 1개 제외하고 모두 기발송 처리
            sent_deals.add(d['id'])
        save_sent_deals(sent_deals)

    last_post_time = 0.0

    # Render 클라우드 Web Service 무료 티어 유지를 위한 헬스체크 서버 가동
    threading.Thread(target=start_health_check_server, daemon=True).start()

    if args.once:
        run_pipeline(sent_deals, last_post_time)
        return

    try:
        while True:
            _, last_post_time = run_pipeline(sent_deals, last_post_time)
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[알림] 사용자에 의해 봇이 안전하게 중단되었습니다.")
        save_sent_deals(sent_deals)

if __name__ == "__main__":
    main()
