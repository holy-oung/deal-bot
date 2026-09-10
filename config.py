# config.py
# 핫딜 봇 환경 설정 파일

# 1. 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN = "8755228376:AAFrFW7YEOhMAsMtbfAkcj54MVzc4jImUIA"
TELEGRAM_CHAT_ID = "7255527272"

# 2. 쿠팡 파트너스 설정
COUPANG_AF_ID = "AF9052431"

# 3. 크롤링 및 알림 설정
CHECK_INTERVAL_SECONDS = 60   # 1분(60초)마다 새 핫딜 확인
MAX_HISTORY_ITEMS = 1000      # 중복 방지 기록 최대 보관 수

# (선택) 특정 키워드만 알림 받고 싶을 때 추가 (비어있으면 전체 핫딜 수집)
# 예: ["라면", "커피", "생수", "모니터", "맥북"]
KEYWORD_FILTERS = []
