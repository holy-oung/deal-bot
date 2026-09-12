# trend_analyzer.py
# 시계열 머신러닝 트렌드 분석기 (Time-decay & Trend Drift Learning Engine)

import os
import sys
import json
import math
import re
from datetime import datetime, timezone, timedelta
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

TIMELINE_FILE = 'trend_timeline.jsonl'
OUTPUT_POOL_FILE = 'dynamic_hook_pool.json'

# 머신러닝 시간 감쇄 파라미터
HALF_LIFE_DAYS = 14.0       # 트렌드 가중치 반감기 (14일)
LAMBDA_DECAY = math.log(2) / HALF_LIFE_DAYS

# 카테고리 식별용 시그니처 키워드
CATEGORY_SIGNATURES = {
    'SHOES': ['러닝', '런닝', '운동화', '신발', '스니커즈', '트레킹화', '등산화', '조던', '크록스'],
    'DIGITAL_TECH': ['헤드셋', '이어폰', '에어팟', '버즈', '키보드', '마우스', '사플', '배그', '발로란트', '독거미', '모니터', '노트북', '충전기', 'it'],
    'LIVING': ['세제', '섬유유연제', '빨래', '땀냄새', '휴지', '화장지', '물티슈', '다우니', '생필품', '자취'],
    'FOOD_PROCESSED': ['라면', '만두', '피자', '치킨', '야식', '밀키트', '배달비', '스팸', '즉석밥', '안주'],
    'FOOD_FRESH': ['소고기', '한우', '삼겹살', '닭가슴살', '과일', '식단', '단백질', '오운완', '계란'],
    'BEVERAGE_SNACK': ['커피', '원두', '캡슐', '아메리카노', '제로', '탄산수', '음료', '홈카페', '과자'],
    'BEAUTY': ['화장품', '피부', '선크림', '수분크림', '올영', '진정', '보습', '앰플', '세럼'],
    'KIDS': ['아이', '육아', '아동', '키즈', '등원룩', '기저귀', '장난감', '유모차'],
    'HOME_APPLIANCE': ['가전', '청소기', '로봇청소기', '에어컨', '드라이기', '공기청정기', '삶의 질'],
    'FASHION': ['옷', '자켓', '패딩', '바람막이', '맨투맨', '후드', '바지', '출근룩', '고프코어']
}

# 기본 시드 템플릿 (콜드스타트 방지 및 기본 베이스라인)
BASE_SEED_HOOKS = {
    'SHOES': [
        {"hook": "요즘 러닝 많이 뛰는데 일반 운동화 신고 뛰는 사람 손? 🏃", "weight": 0.6},
        {"hook": "러닝 크루 들어가려고 가성비 런닝화 찾고 있었다면 👟", "weight": 0.5},
        {"hook": "제발 브랜드 러닝화 정가 10만원씩 다 주고 사지 마세요 🫢", "weight": 0.7}
    ],
    'DIGITAL_TECH': [
        {"hook": "요즘 배그나 발로란트 할 때 사플 안 돼서 답답했던 사람? 🎧", "weight": 0.7},
        {"hook": "게임할 때 선 걸리적거리고 충전 깜빡해서 꺼진 적 다들 있지? 🎧", "weight": 0.6},
        {"hook": "충전독까지 주는 무선 헤드셋인데 이 가격이면 담당자 실수인 듯 🫢", "weight": 0.8}
    ],
    'LIVING': [
        {"hook": "요즘 러닝·헬스하느라 땀 많이 날 텐데 땀냄새 싹 지우려면 이거 써야 함 🧼", "weight": 0.7},
        {"hook": "단가 계산기 두드려봤더니 마트/다이소 반값도 안 나옴 🧼", "weight": 0.8},
        {"hook": "어차피 매달 쓰는 건데 마트 가서 제값 다 주면 제일 속 쓰린 생필품 🧻", "weight": 0.6}
    ],
    'FOOD_PROCESSED': [
        {"hook": "퇴근하고 밥 차리기 귀찮을 때 배달비 아끼는 치트키 🍜", "weight": 0.8},
        {"hook": "주말에 넷플릭스 보면서 맥주 한잔 곁들일 꿀맛 안주 찾는다면 🍺", "weight": 0.7},
        {"hook": "배달앱 켤 때마다 2~3만원씩 깨지는데 이럴 때 냉동실 채워둬야 함 🥟", "weight": 0.7}
    ],
    'FOOD_FRESH': [
        {"hook": "운동하는 사람 손!! 식단 나랑 같이하자 💪", "weight": 0.8},
        {"hook": "오운완 후 단백질 채워둘 식단 비상식량 최저가 떴음 🍗", "weight": 0.7},
        {"hook": "요즘 장바구니 과일 물가 살벌한데 마트 반값 수준으로 풀림 🍎", "weight": 0.6}
    ],
    'BEVERAGE_SNACK': [
        {"hook": "하루 커피 2잔씩 마시는데 매달 커피값 10만원씩 깨지는 사람? ☕", "weight": 0.8},
        {"hook": "운동 끝나고 시원하게 마실 제로 음료 박스로 채워둘 타이밍 🧊", "weight": 0.7},
        {"hook": "물·음료 떨어질 때마다 무겁게 들고 오지 말고 박스로 쟁여둘 타이밍 🧃", "weight": 0.6}
    ],
    'BEAUTY': [
        {"hook": "올영 세일 때도 이 가격은 안 나왔으니 정가 주지 마세요 💄", "weight": 0.8},
        {"hook": "야외 러닝이나 운동하고 자외선에 지친 피부 진정시킬 타이밍 🧴", "weight": 0.7}
    ],
    'KIDS': [
        {"hook": "애들은 금방 쑥쑥 커서 옷 제값 다 주고 사면 제일 아까움 👶", "weight": 0.8},
        {"hook": "브랜드 키즈 의류가 보세 옷보다 싸게 풀린 거 실화인가 👀", "weight": 0.7}
    ],
    'HOME_APPLIANCE': [
        {"hook": "퇴근 후 집안일 시간 확 줄여주는 삶의 질 상승 가전 🏠", "weight": 0.7},
        {"hook": "이 가격에 이 기능이면 진작 살 걸 그랬음... 가성비 종결 🔥", "weight": 0.8}
    ],
    'FASHION': [
        {"hook": "백화점 브랜드 옷 정가 다 주고 사면 바보 되는 이유 👀", "weight": 0.8},
        {"hook": "요즘 유행하는 고프코어/러닝용으로 편하게 입을 기본템 찾는다면 👕", "weight": 0.7}
    ],
    'GENERAL': [
        {"hook": "살까 말까 고민하면서 장바구니에만 넣어뒀던 분들 주목 👀", "weight": 0.7},
        {"hook": "제발 제값 다 주고 사지 마세요! 실시간 최저가 떴습니다 🔥", "weight": 0.8},
        {"hook": "담당자가 할인 쿠폰 중복 적용 풀어둔 듯... 실시간 품절 각 ⚡", "weight": 0.9}
    ]
}

def parse_iso_datetime(dt_str: str) -> datetime:
    """ISO 8601 문자열을 timezone-aware datetime 객체로 파싱"""
    try:
        # Python 3.11+ fromisoformat handles most formats
        return datetime.fromisoformat(dt_str)
    except Exception:
        # Fallback to KST default
        return datetime.now(timezone(timedelta(hours=9)))

def calculate_time_decay_weight(collected_at_str: str, now: datetime) -> float:
    """머신러닝 시간 감쇄 공식 적용: w = e^(-lambda * delta_days)"""
    collected_time = parse_iso_datetime(collected_at_str)
    delta = now - collected_time
    delta_days = max(0.0, delta.total_seconds() / 86400.0)
    
    decay_weight = math.exp(-LAMBDA_DECAY * delta_days)
    return round(decay_weight, 4)

def detect_category(text: str) -> str:
    """텍스트 내용에서 적합한 상품/라이프스타일 카테고리 판별"""
    clean = text.lower()
    scores = {}
    for cat, kws in CATEGORY_SIGNATURES.items():
        match_count = sum(1 for kw in kws if kw in clean)
        if match_count > 0:
            scores[cat] = match_count
            
    if scores:
        return max(scores, key=scores.get)
    return 'GENERAL'

def clean_hook_text(first_line: str) -> str:
    """후킹 텍스트 정제 및 군더더기 제거"""
    t = first_line.strip()
    # 번호나 기호 정제 (예: 1., [추천], 등)
    t = re.sub(r'^\d+[\.\)]\s*', '', t)
    t = re.sub(r'\[.*?\]', '', t)
    return t.strip()

def run_trend_analysis():
    print("🧠 [트렌드 학습 엔진] 시계열 데이터 분석 및 시간 감쇄 가중치 산출 시작...")
    
    if not os.path.exists(TIMELINE_FILE):
        print(f"⚠️ {TIMELINE_FILE} 파일이 없습니다. 기본 베이스라인으로 풀을 구성합니다.")
        save_hook_pool(BASE_SEED_HOOKS, {})
        return

    now = datetime.now(timezone(timedelta(hours=9)))
    
    # 1. 시계열 데이터 로드
    records = []
    with open(TIMELINE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    continue
                    
    print(f"  -> 총 누적 시계열 데이터: {len(records)}건")
    if not records:
        save_hook_pool(BASE_SEED_HOOKS, {})
        return

    # 2. 시간 감쇄 점수 계산 및 카테고리별 후킹 점수 집계
    category_learned_hooks = defaultdict(list)
    recent_keywords = defaultdict(float)

    for r in records:
        content = r.get('content', '')
        first_line = clean_hook_text(r.get('first_line', ''))
        collected_at = r.get('collected_at', now.isoformat())
        likes = r.get('likes', 10)
        replies = r.get('replies', 2)

        if not first_line or len(first_line) < 10:
            continue

        # 시간 감쇄 가중치 (0.0 ~ 1.0)
        decay_w = calculate_time_decay_weight(collected_at, now)
        
        # 인게이지먼트 복합 스코어 (최신일수록 점수가 높고, 오래될수록 감쇄)
        base_score = math.log1p(likes + replies * 2)
        final_score = round(base_score * decay_w, 3)

        category = detect_category(f"{first_line} {content}")
        
        category_learned_hooks[category].append({
            'hook': first_line,
            'weight': final_score,
            'source_account': r.get('account', 'benchmark'),
            'decay_factor': decay_w,
            'collected_at': collected_at
        })

        # 최근 7일 내의 핵심 어휘 가중치 집계 (트렌드 키워드)
        if decay_w >= 0.7:
            for kw in re.findall(r'[가-힣]{2,}', first_line):
                if kw not in ['있는', '하는', '사람', '진짜', '이거', '지금', '어떻게']:
                    recent_keywords[kw] += final_score

    # 3. 베이스라인 시드와 학습된 동적 후킹 융합 (Ensemble Blending)
    final_pool = {}
    all_categories = set(BASE_SEED_HOOKS.keys()).union(category_learned_hooks.keys())

    for cat in all_categories:
        merged = []
        seen_hooks = set()

        # 학습된 고반응 최신 후킹 먼저 정렬하여 추가
        learned = sorted(category_learned_hooks.get(cat, []), key=lambda x: x['weight'], reverse=True)
        for item in learned:
            norm = item['hook'].replace(' ', '')
            if norm not in seen_hooks:
                seen_hooks.add(norm)
                merged.append({
                    'hook': item['hook'],
                    'weight': round(item['weight'], 2),
                    'source': f"@{item['source_account']}"
                })

        # 베이스라인 시드 템플릿 보강 (학습 데이터가 부족하거나 다양성을 보장하기 위함)
        for seed in BASE_SEED_HOOKS.get(cat, []):
            norm = seed['hook'].replace(' ', '')
            if norm not in seen_hooks:
                seen_hooks.add(norm)
                merged.append({
                    'hook': seed['hook'],
                    'weight': seed['weight'],
                    'source': 'seed_baseline'
                })

        # 상위 점수 순으로 정렬 후 상위 10개 풀 유지
        merged.sort(key=lambda x: x['weight'], reverse=True)
        final_pool[cat] = merged[:10]

    # 4. 급상승 트렌드 키워드 Top 10
    top_keywords = sorted(recent_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
    trend_meta = {
        'last_updated': now.isoformat(),
        'half_life_days': HALF_LIFE_DAYS,
        'total_timeline_records': len(records),
        'top_emerging_keywords': [kw for kw, score in top_keywords]
    }

    save_hook_pool(final_pool, trend_meta)

def save_hook_pool(hook_pool: dict, meta: dict):
    output_data = {
        'metadata': meta,
        'hooks': hook_pool
    }
    with open(OUTPUT_POOL_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"✅ [동적 후킹 풀 갱신 완료] {OUTPUT_POOL_FILE}에 최신 트렌드 가중치가 반영되었습니다.")
    if 'top_emerging_keywords' in meta:
        print(f"🔥 최근 급상승 트렌드 키워드: {', '.join(meta['top_emerging_keywords'][:6])}")

if __name__ == '__main__':
    run_trend_analysis()
