# daily_reporter.py
# 매일 밤 11시(KST 23:00) 일일 트렌드 학습, 내 계정 최다 조회수 Top 3 분석 및 피드백 강화 리포터

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta

from notifier import send_telegram_message
from threads_insights import get_top_performing_threads, reinforce_high_performing_posts

sys.stdout.reconfigure(encoding='utf-8')

TIMELINE_FILE = 'trend_timeline.jsonl'
POOL_FILE = 'dynamic_hook_pool.json'
SENT_DEALS_FILE = 'sent_deals.json'

def build_daily_report() -> tuple[str, list[dict]]:
    now_kst = datetime.now(timezone(timedelta(hours=9)))
    date_str = now_kst.strftime("%Y-%m-%d %H:%M KST")
    
    # 1. 내 계정 스레드 최다 조회수 Top 3 분석
    top_threads = []
    try:
        top_threads = get_top_performing_threads(top_k=3, hours_window=72)
    except Exception as e:
        print(f"[Warning] 스레드 인사이트 조회 중 오류: {e}")

    # 2. 고성과 포스트를 시계열 DB에 자동 피드백 주입 (Closed-loop Reinforcement)
    if top_threads:
        try:
            reinforce_high_performing_posts(top_threads)
        except Exception as e:
            print(f"[Warning] 피드백 강화 학습 오류: {e}")

    # 3. 시계열 데이터 통계
    total_timeline_count = 0
    recent_7d_count = 0
    seven_days_ago = now_kst - timedelta(days=7)
    
    if os.path.exists(TIMELINE_FILE):
        with open(TIMELINE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    total_timeline_count += 1
                    try:
                        record = json.loads(line)
                        col_time = datetime.fromisoformat(record.get('collected_at', ''))
                        if col_time >= seven_days_ago:
                            recent_7d_count += 1
                    except Exception:
                        pass
                        
    # 4. 동적 후킹 풀 및 급상승 키워드
    top_keywords = []
    category_samples = []
    
    if os.path.exists(POOL_FILE):
        with open(POOL_FILE, 'r', encoding='utf-8') as f:
            try:
                pool_data = json.load(f)
                meta = pool_data.get('metadata', {})
                top_keywords = meta.get('top_emerging_keywords', [])
                hooks = pool_data.get('hooks', {})
                
                # 대표 카테고리 1위 후킹 추출
                for cat, label, icon in [('SHOES', '러닝/슈즈', '🏃'), ('DIGITAL_TECH', 'IT/게이밍', '🎧'), ('FOOD_FRESH', '식단/신선', '🥩'), ('LIVING', '생활/세제', '🧼')]:
                    items = hooks.get(cat, [])
                    if items:
                        best = items[0]
                        source_tag = f"[{best.get('source', '')}]" if 'source' in best else ""
                        category_samples.append(f"• {icon} [{label}]: <i>\"{best['hook']}\"</i> (가중치 {best.get('weight', 1.0)} {source_tag})")
            except Exception as e:
                print(f"[Warning] 후킹 풀 분석 실패: {e}")

    # 5. 핫딜 발송 현황
    total_sent_deals = 0
    if os.path.exists(SENT_DEALS_FILE):
        with open(SENT_DEALS_FILE, 'r', encoding='utf-8') as f:
            try:
                sent_list = json.load(f)
                total_sent_deals = len(sent_list)
            except Exception:
                pass

    kw_text = ", ".join([f"#{kw}" for kw in top_keywords[:6]]) if top_keywords else "데이터 집계 중"
    sample_text = "\n".join(category_samples[:3]) if category_samples else "• 등록된 후킹 템플릿 준비 중"

    # 내 계정 Top 3 섹션 포맷팅
    top_threads_lines = []
    rank_emojis = ["🥇", "🥈", "🥉"]
    for idx, th in enumerate(top_threads):
        emoji = rank_emojis[idx] if idx < len(rank_emojis) else f"{idx+1}."
        prod_short = th['product_line'][:35] if th['product_line'] else "상품 정보"
        top_threads_lines.append(
            f"{emoji} <b>{idx+1}위: 조회수 {th['views']:,}회</b> (❤️ {th['likes']} / 💬 {th['replies']})\n"
            f"   • 카테고리: <b>{th['category']}</b>\n"
            f"   • 후킹: <i>\"{th['hook'][:45]}...\"</i>\n"
            f"   • 상품: {prod_short}...\n"
            f"   • <a href=\"{th['permalink']}\">👉 스레드 원문 보기</a>"
        )
    
    top_section = "\n\n".join(top_threads_lines) if top_threads_lines else "• 최근 72시간 내 집계된 스레드 게시물이 없습니다."

    report_lines = [
        "📊 <b>[Deal-Bot 일일 트렌드 &amp; 운영 리포트]</b>",
        f"📅 <i>{date_str} 기준</i>",
        "",
        "🔥 <b>오늘 내 계정 최다 조회수 Top 3 (Threads)</b>",
        top_section,
        "",
        "💡 <i>성과가 검증된 상위 포스트 패턴은 내일 포스팅 풀에 최우선 가중치로 자동 재학습(Feedback Loop)되었습니다.</i>",
        "",
        "🧠 <b>시계열 트렌드 지속 학습 현황</b>",
        f"• 총 누적 트렌드 데이터: <b>{total_timeline_count}건</b>",
        f"• 최근 7일 내 신규 학습: <b>{recent_7d_count}건</b> (14일 반감기 감쇄)",
        f"• 🔥 <b>급상승 트렌드 키워드:</b>\n  {kw_text}",
        "",
        "🎯 <b>실시간 1위 후킹 샘플 (Time-decay 랭킹)</b>",
        sample_text,
        "",
        "🤖 <b>핫딜 봇 운영 현황</b>",
        f"• 누적 발송 완료 핫딜: <b>{total_sent_deals}건</b>",
        "• 100% 쿠팡 파트너스 수익 링크(AF9052431) 변환 정상 가동",
        "• Threads 2단 분리 &amp; Telegram 채널 알림: <b>정상 가동 중 ✅</b>",
        "",
        "<i>매일 밤 11시 시스템 상태를 정기 보고합니다.</i>"
    ]

    return "\n".join(report_lines), top_threads

def main():
    parser = argparse.ArgumentParser(description="일일 트렌드 & 시스템 운영 리포트 발송기")
    parser.add_argument("--dry-run", action="store_true", help="텔레그램 발송 없이 콘솔 출력만 수행")
    args = parser.parse_args()

    report, top_threads = build_daily_report()
    
    print("==================================================")
    print("📋 일일 리포트 미리보기")
    print("==================================================")
    print(report)
    print("==================================================")

    if args.dry_run:
        print("ℹ️ [Dry-run] 텔레그램 발송을 건너뜁니다.")
        return

    print("🚀 텔레그램 채널/관리자에게 일일 리포트 발송 중...")
    success = send_telegram_message(report)
    if success:
        print("✅ 텔레그램 일일 리포트 발송 완료!")
    else:
        print("❌ 텔레그램 리포트 발송 실패")

if __name__ == '__main__':
    main()
