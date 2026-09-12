# notifier.py
# 텔레그램 알림 메시지 발송 모듈 (간결한 3단 구조: 후킹글 + 가격 + 단일 제품링크)

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_deal_alert(deal: dict, formatted_message: str) -> bool:
    """
    [후킹성 원글 + 가격 분석 + 제품 링크] 3단 구조 메시지 전송
    잡다한 버튼 없이 깔끔하게 링크만 포함
    """
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'parse_mode': 'HTML',
    }
    
    try:
        if deal.get('thumb_url'):
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            payload['photo'] = deal['thumb_url']
            payload['caption'] = formatted_message
            res = requests.post(url, json=payload, timeout=10)
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload['text'] = formatted_message
            payload['disable_web_page_preview'] = False
            res = requests.post(url, json=payload, timeout=10)
            
        data = res.json()
        return data.get('ok', False)
    except Exception as e:
        print(f"[Error] 텔레그램 발송 실패: {e}")
        return False

def send_telegram_message(text: str) -> bool:
    """일반 텍스트/HTML 리포트 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        return data.get('ok', False)
    except Exception as e:
        print(f"[Error] 텔레그램 메시지 발송 실패: {e}")
        return False

