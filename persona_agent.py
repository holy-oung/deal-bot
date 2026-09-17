# persona_agent.py
# 계정 웜업용 스레드 일상글 자동 생성 에이전트

import random
import google.generativeai as genai
from config import GEMINI_API_KEY

# API 키가 없거나 할당량 초과 시 사용할 고품질 Fallback 데이터셋 (2030 한국인 감성 100%)
FALLBACK_POSTS = [
    "비 오니까 출근길 지옥철 벌써부터 두렵다.. 다들 우산 챙기셨나요 ㅠㅠ",
    "오늘 점심은 무조건 제육이다. 직장인 점심메뉴 국룰 인정? ㅋㅋ",
    "월요일 아침부터 회의 3개 연속.. 정신 나가겠네 😇 커피 수혈 시급함",
    "요즘 날씨 왜 이러지? 어제는 덥더니 오늘은 춥고.. 옷 입기 너무 애매함",
    "퇴근 마렵다.. 아직 3시밖에 안 됐다니 시계 고장난 거 아님? ⏰",
    "주말에 하루종일 넷플릭스만 보고 누워있었는데 벌써 일요일 밤이라니 ㅠㅠ",
    "아침에 알람 못 들어서 지각할 뻔.. 땀 뻘뻘 흘리면서 뛰어옴 🏃‍♂️💨",
    "요즘 런닝 시작했는데 작심삼일 될까봐 걱정.. 오운완 성공하신 분들 팁 좀요!",
    "퇴근하고 치맥 땡기는데 같이 먹을 사람이 없네.. 혼맥이나 해야겠다 🍺",
    "배달비 너무 비싸서 포장하러 나왔는데 걷기 귀찮아 죽겠음.. ㅋㅋㅋ"
]

def generate_daily_life_post() -> str:
    """
    LLM을 사용하여 한국인 2030 페르소나의 일상글 생성.
    API 호출 실패 시 Fallback 데이터셋 사용.
    """
    if not GEMINI_API_KEY:
        return random.choice(FALLBACK_POSTS)

    genai.configure(api_key=GEMINI_API_KEY)
    
    generation_config = {
        "temperature": 0.8,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 150,
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
    )
    
    prompt = """
    당신은 한국의 20대~30대 평범한 직장인/대학생입니다.
    스레드(Threads)에 올릴 짧고 자연스러운 일상글을 딱 1~2문장으로 작성해주세요.
    
    [규칙]
    1. 해시태그 절대 금지, 이모지 1~2개만 자연스럽게 사용.
    2. 너무 작위적이거나 AI 티가 나는 명언, 긍정적인 다짐 금지.
    3. 퇴근 마려움, 점심 고민, 피곤함, 지옥철, 주말 순삭, 날씨 투정 등 현실적인 한국인 감성.
    4. 친근한 반말이나 편한 존댓말 섞어서 사용.
    5. 바로 복사해서 올릴 수 있도록 텍스트만 출력하세요.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = text.strip('"').strip("'")
        if text:
            return text
    except Exception as e:
        print(f"[Persona Agent] LLM 생성 실패, Fallback 사용: {e}")
        
    return random.choice(FALLBACK_POSTS)

if __name__ == "__main__":
    print(generate_daily_life_post())
