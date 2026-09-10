# config.py
# 핫딜 봇 환경 설정 파일

import os

# .env 파일이 존재하는 경우 자동으로 환경변수 로드
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

# 1. 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8755228376:AAFrFW7YEOhMAsMtbfAkcj54MVzc4jImUIA")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7255527272")

# 2. 쿠팡 파트너스 설정
COUPANG_AF_ID = os.getenv("COUPANG_AF_ID", "AF9052431")

# 3. 스레드(Threads) API 설정 (Meta Graph API)
# .env 파일이나 GitHub Actions Secrets에서 로드됩니다.
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN", "")
THREADS_USER_ID = os.getenv("THREADS_USER_ID", "")
ENABLE_THREADS_POSTING = os.getenv("ENABLE_THREADS_POSTING", "true").lower() in ("true", "1", "yes")



# 4. 크롤링 및 알림 설정
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))   # 1분(60초)마다 새 핫딜 확인
MAX_HISTORY_ITEMS = int(os.getenv("MAX_HISTORY_ITEMS", "1000"))          # 중복 방지 기록 최대 보관 수

# (선택) 특정 키워드만 알림 받고 싶을 때 추가 (비어있으면 전체 핫딜 수집)
# 예: ["라면", "커피", "생수", "모니터", "맥북"]
KEYWORD_FILTERS = []

