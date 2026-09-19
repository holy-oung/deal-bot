import sys
import re
import random
from google import genai
from google.genai import types
from datetime import datetime, timezone, timedelta
from config import GEMINI_API_KEY

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

WEEKDAY_KOREAN = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

def clean_post_text(raw_text: str) -> str:
    """
    LLM 응답에서 메타 헤더, Thinking 라벨, 포맷 텍스트, 따옴표 등을 완벽히 제거하는 정제기
    """
    if not raw_text:
        return ""
        
    text = raw_text.strip()
    
    # 1. 서두에 붙는 메타 라벨 제거 (예: (Output Format):**, **Output Format:**, 본문:, Thread:, Context: 등)
    meta_patterns = [
        r'^\s*\(?(?:Output\s*Format|Format|Output|본문|스레드\s*본문|스레드|답변|내용|Context|Tone|Here is the post)\)?\s*[:*]{1,3}\s*',
        r'^\s*\*\*(?:Output\s*Format|본문|스레드|내용)\*\*\s*[:\-]?\s*',
        r'^\s*\[(?:Output\s*Format|본문|스레드|내용)\]\s*[:\-]?\s*'
    ]
    for pat in meta_patterns:
        text = re.sub(pat, '', text, flags=re.IGNORECASE).strip()
        
    # 2. 앞뒤 큰따옴표, 작은따옴표, 마크다운 볼드 잔여 기호 제거
    text = text.strip('"\'`* \t\r\n')
    
    # 3. 여러 줄로 나온 경우 본문 첫 1~2줄만 결합
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        # 혹시 첫 줄이 또 메타 헤더로 시작하면 제외
        valid_lines = []
        for line in lines:
            cleaned_line = re.sub(r'^\s*\(?(?:Output\s*Format|Context|Tone)\)?\s*[:*]*\s*', '', line, flags=re.IGNORECASE).strip()
            if cleaned_line and not any(cleaned_line.lower().startswith(p) for p in ['output format', 'context:', 'tone:']):
                valid_lines.append(cleaned_line)
        text = " ".join(valid_lines[:2])
    
    return text.strip('"\'`* \t\r\n')

def get_fallback_post() -> str:
    """
    API 오류나 할당량 초과 시 사용할 안전 Fallback 데이터셋 (평일 vs 주말/요일 감성 100% 반영)
    """
    # KST 기준 시간 및 요일 계산
    kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
    hour = kst_now.hour
    is_weekend = kst_now.weekday() >= 5  # 토(5), 일(6)
    is_sunday = kst_now.weekday() == 6
    
    if is_weekend:
        if 6 <= hour < 12:
            return random.choice([
                "주말에 알람 안 맞추고 눈 떴을 때가 세상에서 제일 행복함.. 뒹굴뒹굴 더 잘래 😴",
                "주말 아침엔 역시 느지막이 일어나서 마시는 아이스 아메리카노가 최고 ☕",
                "평일엔 그렇게 안 떠지던 눈이 주말엔 왜 이렇게 일찍 떠지는지 미스터리.. ㅋㅋㅋ"
            ])
        elif 12 <= hour < 17:
            return random.choice([
                "늦점 먹고 배 두드리면서 침대 누워있는데 벌써 오후라니.. 주말 시간 순삭 실화? 🫠",
                "날씨 너무 좋아서 카페나 슬슬 마실 나가볼까 고민 중 🌿",
                "주말엔 침대랑 한 몸 되는 게 국룰이지.. 오늘 아무것도 안 할 거임 ㅋㅋㅋ"
            ])
        elif 17 <= hour < 22:
            if is_sunday:
                return random.choice([
                    "벌써 일요일 저녁이라니.. 내일 월요일인 거 실화냐? 주말 돌려줘요 ㅠㅠ",
                    "일요일 밤 특: 갑자기 월요병 도지고 심장 빨리 뜀.. 주말 3일제 시급하다 😇",
                    "일요일 저녁은 역시 맛있는 배달음식으로 월요병 미리 치유하기 🍕"
                ])
            else: # 토요일
                return random.choice([
                    "토요일 저녁이 일주일 중에 제일 마음 편함.. 맛있는 거 시켜 먹고 푹 쉬어야지 🍗🍺",
                    "주말 저녁 바람 쐬러 나왔는데 날씨 딱 좋네! 다들 좋은 주말 보내세요 ✨",
                    "토요일 밤 넷플릭스 정주행 준비 완료.. 오늘 새벽까지 안 잔다 🎬"
                ])
        else: # 22시 이후
            if is_sunday:
                return random.choice([
                    "내일 출근해야 하는데 잠이 안 와서 큰일났다.. 잠 드는 법 까먹음 ㅋㅋㅋ 😇",
                    "일요일 밤 보내기 너무 아쉬워서 폰만 만지작거리는 중.. 다들 월요팅입니다 🌙"
                ])
            else:
                return random.choice([
                    "내일도 쉰다는 사실이 너무 짜릿하다.. 토요일 밤 최고야 🌙",
                    "주말 넷플릭스 정주행 하느라 수면패턴 다 망가짐 ㅋㅋㅋ 다들 굿밤되세요!"
                ])
    else:
        # 평일 감성
        if 6 <= hour < 12:
            return random.choice([
                "아침에 알람 못 들어서 지각할 뻔.. 땀 뻘뻘 흘리면서 뛰어옴 🏃‍♂️💨",
                "출근길 지옥철 진짜 숨막힌다.. 다들 오늘 하루도 화이팅 ㅠㅠ",
                "아침부터 회의 연속.. 정신 나가겠네 😇 모닝 커피 수혈 시급함 ☕"
            ])
        elif 12 <= hour < 17:
            return random.choice([
                "오늘 점심은 무조건 제육이다. 직장인 점심메뉴 국룰 인정? ㅋㅋ",
                "밥 먹고 나니까 식곤증 장난 아니네.. 퇴근 마렵다 😪",
                "오후 되니까 당 떨어지네.. 아이스 아메리카노 하나 때려야겠다 ☕"
            ])
        elif 17 <= hour < 22:
            return random.choice([
                "퇴근 마렵다.. 시간 왜 이렇게 안 가냐 시계 고장난 거 아님? ⏰",
                "퇴근하고 시원한 치맥 한잔 때리러 갑니다.. 오늘 하루도 고생 많으셨어요 🍺",
                "배달비 너무 비싸서 포장하러 나왔는데 걷기 귀찮아 죽겠음.. ㅋㅋㅋ"
            ])
        else:
            return random.choice([
                "아직 안 자고 폰 보는 사람? 내일 출근 우짜지 ㅋㅋㅋ",
                "요즘 런닝 시작했는데 작심삼일 될까봐 걱정.. 오운완 성공하신 분들 팁 좀요!",
                "오늘 하루도 다들 고생 많으셨습니다. 푹 쉬고 내일 또 힘내요 🌙"
            ])

def generate_daily_life_post() -> str:
    """
    Gemini 3.6 Flash를 사용하여 한국인 2030 페르소나의 일상글 생성.
    평일/주말 요일과 시간대 감성을 완벽히 반영하며, 토큰 잘림 방지 및 텍스트 클리닝 적용.
    """
    if not GEMINI_API_KEY:
        return get_fallback_post()

    # KST 기준 일시 계산
    kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
    weekday_str = WEEKDAY_KOREAN[kst_now.weekday()]
    is_weekend = kst_now.weekday() >= 5
    current_time_str = kst_now.strftime(f"%Y년 %m월 %d일 ({weekday_str}) %H시 %M분")

    situation_guide = (
        f"[상황: 여유로운 주말({weekday_str})]\n"
        "오늘은 꿀 같은 주말입니다! 주말 특유의 라이프스타일(늦잠, 뒹굴거리기, 브런치/배달음식, 카페, 산책, 나들이, OTT 정주행, 주말 순삭의 아쉬움 등)에 딱 맞는 공감 일상글을 작성하세요."
        if is_weekend else
        f"[상황: 평일({weekday_str})]\n"
        "오늘은 평일입니다. 현재 시간대(출근길, 오전 업무, 점심 메뉴, 오후 졸음/식곤증, 퇴근길, 저녁 휴식 등)의 현실적인 직장인/대학생 공감 일상글을 작성하세요."
    )

    prompt = f"""
당신은 한국의 20대~30대 평범한 사람(직장인/대학생)입니다.
현재 시간은 {current_time_str} 입니다.

{situation_guide}

스레드(Threads)에 올릴 짧고 매력적인 일상글을 딱 1~2문장으로 작성해주세요.

[규칙]
1. 요일({weekday_str})과 시간대({kst_now.hour}시)의 감성에 완벽하게 부합해야 합니다.
2. 해시태그 절대 금지, 이모지 1~2개만 자연스럽게 사용.
3. 너무 작위적이거나 AI 티가 나는 명언, 억지 긍정주의 금지.
4. 친근한 반말이나 편한 존댓말 섞어서 2030 커뮤니티 감성으로 작성.

[가장 중요한 출력 조건]
- 생각 과정(Thinking)이나 메타 설명, 라벨(예: Output Format:, 본문:, Context:)을 절대로 출력하지 마세요.
- 큰따옴표(")로 묶지 말고, 스레드에 바로 올릴 수 있는 순수한 텍스트 본문 단 1~2문장만 출력하세요.
"""

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.85,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1000,  # Thinking 토큰 포함으로 인한 잘림 방지
            )
        )
        raw_text = response.text if response.text else ""
        cleaned = clean_post_text(raw_text)
        
        # 5글자 이상이고 정상적인 한글 텍스트인 경우 채택
        if cleaned and len(cleaned) >= 5:
            return cleaned
        else:
            print(f"[Persona Agent] 정제 결과 텍스트가 너무 짧거나 부적절함: '{cleaned}' -> Fallback 사용")
    except Exception as e:
        print(f"[Persona Agent] LLM 생성 실패, Fallback 사용: {e}")
        
    return get_fallback_post()

if __name__ == "__main__":
    print("생성된 일상글:")
    for _ in range(3):
        print(" ->", generate_daily_life_post())
