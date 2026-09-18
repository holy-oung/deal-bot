import sys
import random
from google import genai
from google.genai import types
from datetime import datetime
from config import GEMINI_API_KEY

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_fallback_post() -> str:
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return random.choice([
            "아침에 알람 못 들어서 지각할 뻔.. 땀 뻘뻘 흘리면서 뛰어옴 🏃‍♂️💨",
            "출근길 지옥철 진짜 숨막힌다.. 다들 화이팅 ㅠㅠ",
            "아침부터 회의 3개 연속.. 정신 나가겠네 😇 커피 수혈 시급함"
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
            "퇴근하고 치맥 땡기는데 같이 먹을 사람이 없네.. 혼맥이나 해야겠다 🍺",
            "배달비 너무 비싸서 포장하러 나왔는데 걷기 귀찮아 죽겠음.. ㅋㅋㅋ"
        ])
    else:
        return random.choice([
            "아직 안 자고 폰 보는 사람? 내일 출근 우짜지 ㅋㅋㅋ",
            "요즘 런닝 시작했는데 작심삼일 될까봐 걱정.. 오운완 성공하신 분들 팁 좀요!",
            "주말 넷플릭스 정주행 하느라 수면패턴 다 망가짐 ㅠㅠ 다들 굿밤되세요 🌙"
        ])

def generate_daily_life_post() -> str:
    """
    LLM을 사용하여 한국인 2030 페르소나의 일상글 생성.
    API 호출 실패 시 시간대별 Fallback 데이터셋 사용.
    """
    if not GEMINI_API_KEY:
        return get_fallback_post()

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    current_time_str = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
    
    prompt = f"""
    당신은 한국의 20대~30대 평범한 직장인/대학생입니다.
    현재 시간은 {current_time_str} 입니다.
    스레드(Threads)에 올릴 짧고 자연스러운 일상글을 딱 1~2문장으로 작성해주세요.
    
    [규칙]
    1. 현재 시간대(아침 출근, 점심, 오후 졸음, 퇴근길, 저녁, 심야)에 완벽하게 맞는 내용이어야 합니다.
    2. 해시태그 절대 금지, 이모지 1~2개만 자연스럽게 사용.
    3. 너무 작위적이거나 AI 티가 나는 명언, 긍정적인 다짐 금지.
    4. 친근한 반말이나 편한 존댓말 섞어서 사용.
    
    [가장 중요한 출력 조건]
    반드시 스레드에 업로드할 '본문 텍스트' 단 한 줄(또는 두 줄)만 출력하세요. 
    "Context", "Tone", "Here is the post" 같은 부연 설명이나 메타 데이터를 절대 포함하지 마세요. 큰따옴표(")도 출력하지 마세요.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                top_p=0.95,
                top_k=40,
                max_output_tokens=150,
            )
        )
        text = response.text.strip()
        text = text.strip('"').strip("'")
        if text and not text.lower().startswith("context"):
            return text
    except Exception as e:
        print(f"[Persona Agent] LLM 생성 실패, Fallback 사용: {e}")
        
    return get_fallback_post()

if __name__ == "__main__":
    print(generate_daily_life_post())
