# copywriter.py
# 숏폼/스레드 모바일 스크롤 최적화 트렌드 취미 연계(러닝, 배그 사플, 오운완 식단, 땀냄새 빨래 등) + 초압축 3단 포맷터

import re
import random

# ==========================================
# 1. 카테고리 정의 및 정밀 키워드 매핑
# ==========================================
CATEGORY_KEYWORDS = {
    'SHOES': [
        '신발', '운동화', '스니커즈', '러닝화', '런닝화', '트레킹화', '등산화',
        '슬리퍼', '샌들', '뮬', '로퍼', '구두', '부츠', '워커', '크록스',
        '조던', '덩크', '단화', '블로퍼', '슈즈', '플랫슈즈'
    ],
    'DIGITAL_TECH': [
        '헤드셋', '이어폰', '에어팟', '버즈', '헤드폰', '키보드', '마우스', '모니터',
        '노트북', '랩탑', '맥북', '태블릿', '아이패드', '갤럭시탭', '스마트폰', '아이폰',
        '갤럭시', '충전기', '보조배터리', '케이블', '거치대', '그래픽카드', '글카',
        'rtx', 'cpu', 'ssd', 'ram', '데스크탑', '스마트워치', '애플워치', '갤럭시워치',
        '워치', '스피커', '사운드바', '닌텐도', '플스', '플레이스테이션', 'xbox',
        '독거미', '마이크', '공유기', '게이밍'
    ],
    'HOME_APPLIANCE': [
        '청소기', '로봇청소기', '공기청정기', '가습기', '제습기', '에어컨', '선풍기',
        '서큘레이터', '밥솥', '전자레인지', '오븐', '에어프라이어', '식기세척기',
        '세탁기', '건조기', '헤어드라이어', '드라이기', '면도기', '안마기', 'tv', '티비',
        '비데', '정수기', '인덕션', '전기포트'
    ],
    'BEAUTY': [
        '화장품', '선크림', '선블록', '선스틱', '수분크림', '보습크림', '앰플', '세럼',
        '에센스', '스킨', '토너', '로션', '마스크팩', '클렌징', '클렌징폼', '클렌징오일',
        '립밤', '틴트', '립스틱', '쿠션', '파운데이션', '아이라이너', '마스카라',
        '핸드크림', '바디로션', '향수'
    ],
    'KIDS': [
        '키즈', '아동', '유아', '주니어', '베이비', '어린이', '기저귀', '젖병',
        '분유', '이유식', '장난감', '유모차', '카시트'
    ],
    'LIVING': [
        '세제', '세탁세제', '섬유유연제', '주방세제', '퐁퐁', '락스', '화장지', '휴지',
        '롤휴지', '두루마리', '티슈', '물티슈', '칫솔', '치약', '가글', '샴푸', '린스',
        '트리트먼트', '바디워시', '비누', '크린랩', '위생랩', '매직랩', '호일', '은박지',
        '종이호일', '지퍼백', '위생백', '종이컵', '수건', '타월', '밀폐용기', '반찬통',
        '프라이팬', '후라이팬', '냄비', '건조대', '피죤', '다우니', '퍼실', '리큐', '테크'
    ],
    'FOOD_PROCESSED': [
        '라면', '신라면', '진라면', '짜파게티', '불닭', '너구리', '안성탕면', '비빔면',
        '즉석밥', '햇반', '오뚜기밥', '만두', '교자', '왕교자', '군만두', '물만두',
        '피자', '핫도그', '치킨', '너겟', '가라아게', '팝콘', '떡볶이', '밀키트',
        '전골', '부대찌개', '볶음밥', '스팸', '리챔', '참치캔', '소시지', '비엔나',
        '카레', '짜장', '도시락김', '조미김', '파스타', '시리얼'
    ],
    'FOOD_FRESH': [
        '한우', '소고기', '돼지고기', '삼겹살', '목살', '항정살', '소곱창', '대창', '막창',
        '불고기', '갈비', '닭고기', '닭가슴살', '과일', '감귤', '귤', '사과', '포도',
        '샤인머스캣', '딸기', '수박', '복숭아', '토마토', '참외', '자두', '체리', '망고',
        '오렌지', '한라봉', '천혜향', '레드향', '김치', '포기김치', '장어', '고등어',
        '연어', '새우', '굴', '전복', '오징어', '낙지', '문어', '모듬회', '연어회',
        '백미', '현미', '찹쌀', '햅쌀', '계란', '달걀', '채소', '야채'
    ],
    'BEVERAGE_SNACK': [
        '커피', '원두', '캡슐', '아메리카노', '라떼', '카누', '맥심', '생수', '삼다수',
        '스파클', '탄산수', '탄산음료', '콜라', '제로콜라', '사이다', '음료수', '주스',
        '우유', '두유', '에너지드링크', '과자', '스낵', '초콜릿', '캔디', '젤리', '쿠키', '칩'
    ],
    'FASHION': [
        '점퍼', '자켓', '코트', '패딩', '다운', '바람막이', '맨투맨', '후드', '후디',
        '셔츠', '티셔츠', '니트', '가디건', '팬츠', '바지', '슬랙스', '청바지', '데님',
        '트레이닝', '조거', '속옷', '팬티', '브라', '양말', '가방', '백팩', '숄더백',
        '크로스백', '지갑', '벨트', '모자', '볼캡', '원피스', '스커트', '의류'
    ]
}

def clean_title_for_display(title: str) -> str:
    """쇼핑몰 태그 및 부가 정보를 깔끔하게 정리한 제품명"""
    t = re.sub(r'\[.*?\]', '', title)
    t = re.sub(r'\(.*?\)', '', t)
    t = re.sub(r'\s*/\s*(?:무료|무배|유료|배송비.*)$', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def classify_deal_category(title: str) -> str:
    """상품명을 분석하여 정밀 카테고리 판별 (태그 제거 후 분석)"""
    clean_text = clean_title_for_display(title).lower()
    
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['SHOES']):
        return 'SHOES'
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['DIGITAL_TECH']):
        return 'DIGITAL_TECH'
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['HOME_APPLIANCE']):
        return 'HOME_APPLIANCE'
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['BEAUTY']):
        return 'BEAUTY'
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['KIDS']):
        return 'KIDS'
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['LIVING']):
        return 'LIVING'
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['FOOD_PROCESSED']):
        return 'FOOD_PROCESSED'
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['FOOD_FRESH']):
        return 'FOOD_FRESH'
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['BEVERAGE_SNACK']):
        return 'BEVERAGE_SNACK'
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['FASHION']):
        return 'FASHION'
        
    return 'GENERAL'

def parse_price_and_quantity(title: str):
    """제목에서 가격, 수량, 단위 추출"""
    price = None
    price_match = re.search(r'\(([\d,.]+)\s*(?:원)?\s*\/', title)
    if price_match:
        try:
            raw_p = price_match.group(1).replace(',', '').replace('.', '')
            price = int(raw_p)
        except ValueError:
            price = None
            
    qty = None
    unit = None
    
    qty_matches = re.findall(r'(\d+)\s*(개|봉|봉지|매|팩|입|캔|병|박스|포|롤|세트)', title)
    if qty_matches:
        try:
            qty = sum(int(m[0]) for m in qty_matches)
            unit = qty_matches[0][1]
        except ValueError:
            qty = None
            
    if not qty:
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g)', title, re.IGNORECASE)
        if weight_match:
            val = float(weight_match.group(1))
            unit_str = weight_match.group(2).lower()
            if unit_str == 'kg':
                val = val * 1000
            qty = int(val // 100) if val >= 100 else 1
            unit = '100g'

    return price, qty, unit

# ==========================================
# 2. 동적 머신러닝 후킹 로더 및 가중치 샘플링 엔진
# ==========================================
import os
import json

DYNAMIC_POOL_FILE = os.path.join(os.path.dirname(__file__), 'dynamic_hook_pool.json')
_cached_pool = None
_cached_pool_mtime = 0.0

def load_dynamic_hook_pool() -> dict:
    """dynamic_hook_pool.json 파일을 실시간 캐싱 및 자동 갱신 감지 로드"""
    global _cached_pool, _cached_pool_mtime
    if not os.path.exists(DYNAMIC_POOL_FILE):
        return {}
    try:
        mtime = os.path.getmtime(DYNAMIC_POOL_FILE)
        if _cached_pool is not None and mtime == _cached_pool_mtime:
            return _cached_pool
        with open(DYNAMIC_POOL_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _cached_pool = data.get('hooks', {})
            _cached_pool_mtime = mtime
            return _cached_pool
    except Exception as e:
        print(f"⚠️ [후킹 풀 로드 오류] {e}")
        return _cached_pool or {}

def get_trendy_hook(title: str, category: str) -> str:
    """
    동적으로 학습된 후킹 풀(dynamic_hook_pool.json)에서 
    시간 감쇄 가중치(Score) 기반 확률적 샘플링(Weighted Sampling)으로 최적의 후킹 추출
    """
    pool = load_dynamic_hook_pool()
    candidates = pool.get(category, [])
    
    # 해당 카테고리가 비어있으면 GENERAL 풀 활용
    if not candidates:
        candidates = pool.get('GENERAL', [])
        
    if not candidates:
        # 풀 파일이 없거나 비어있는 경우 안전 폴백
        fallback_hooks = [
            "살까 말까 고민하면서 장바구니에만 넣어뒀던 분들 주목 👀",
            "제발 제값 다 주고 사지 마세요! 실시간 최저가 떴습니다 🔥",
            "담당자가 할인 쿠폰 중복 적용 풀어둔 듯... 실시간 품절 각 ⚡"
        ]
        return random.choice(fallback_hooks)

    # 가중치 기반 샘플링: 최신 트렌드/고반응 후킹일수록 더 높은 확률로 채택
    hooks = [item['hook'] for item in candidates]
    weights = [max(0.1, float(item.get('weight', 1.0))) for item in candidates]
    
    selected = random.choices(hooks, weights=weights, k=1)[0]
    return selected

def build_product_price_line(clean_name: str, price: int | None, qty: int | None, unit: str | None) -> str:
    """물품 소개 + 가격 1줄 생성"""
    if not price:
        return f"👉 {clean_name} 지금 할인 혜택으로 풀렸어!"
        
    raw_est = price * 1.4
    estimated_original = int((raw_est + 499) // 500 * 500)
    if estimated_original <= price:
        estimated_original = price + 1000
    discount_rate = int((estimated_original - price) / estimated_original * 100)

    if qty and qty > 1:
        my_each = price // qty
        use_unit = unit if unit else '개'
        unit_label = "100g에" if use_unit == "100g" else ("1봉에" if use_unit in ['봉', '봉지'] else f"1{use_unit}에")
        return f"👉 {clean_name} {price:,}원 ({unit_label} {my_each:,}원꼴)"
    else:
        return f"👉 {clean_name} {price:,}원 (정상가 대비 {discount_rate}% 할인)"

def extract_deal_context_tag(context_text: str) -> str:
    """원문 맥락(Track 1/2)에서 핵심 구매/할인 조건 태그 추출"""
    if not context_text:
        return ""
    text_lower = context_text.lower()
    if '역대가' in text_lower or '역대급' in text_lower:
        return "🔥 역대급 최저가"
    if '체감가' in text_lower:
        return "✨ 체감가 기준"
    if any(k in text_lower for k in ['카드', '청구할인', '페이']):
        return "💳 결제/카드 혜택"
    if '쿠폰' in text_lower:
        return "🎫 쿠폰 중복적용"
    if '한정' in text_lower:
        return "⚡ 한정 수량 특가"
    return ""

def format_threads_post(title: str, product_link: str, context_text: str = "") -> tuple[str, str]:
    """
    쇼츠/스레드 초압축 3단 포맷터 (듀얼 트랙 정보 해상도 강화):
    1) 트렌드 취미/라이프스타일 연계 공감 후킹 (1줄)
    2) 물품 소개 + 가격 + 핵심 조건 태그 (1줄)
    3) 구매 링크 안내 (1줄)
    """
    clean_name = clean_title_for_display(title)
    category = classify_deal_category(title)
    hook = get_trendy_hook(title, category)
    price, qty, unit = parse_price_and_quantity(title)
    
    product_line = build_product_price_line(clean_name, price, qty, unit)
    
    # 원문 맥락에서 추출한 조건 태그 결합 (정보 해상도 극대화)
    context_tag = extract_deal_context_tag(context_text)
    if context_tag and context_tag not in product_line:
        product_line = f"{product_line} [{context_tag}]"
        
    root_lines = [
        hook,
        product_line,
        "",
        "🔗 구매 좌표는 첫 번째 댓글에 남겨둘게! 👇"
    ]
    root_content = "\n".join(root_lines)
    
    reply_lines = [
        f"👉 실시간 최저가 & 구매 좌표:\n{product_link}",
        "",
        "※ 파트너스 활동의 일환으로 수수료를 제공받을 수 있습니다."
    ]
    reply_content = "\n".join(reply_lines)
    
    return root_content, reply_content

def format_post(title: str, product_link: str) -> str:
    """텔레그램 알림용 포맷터"""
    clean_name = clean_title_for_display(title)
    category = classify_deal_category(title)
    hook = get_trendy_hook(title, category)
    price, qty, unit = parse_price_and_quantity(title)
    
    product_line = build_product_price_line(clean_name, price, qty, unit)
    
    lines = [
        hook,
        f"<b>{product_line}</b>",
        "",
        product_link,
        "",
        "<i>※ 파트너스 활동의 일환으로 수수료를 제공받을 수 있습니다.</i>"
    ]
    return "\n".join(lines)
