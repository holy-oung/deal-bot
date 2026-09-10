# copywriter.py
# 숏폼/스레드 모바일 스크롤 최적화 초압축 4대 후킹 믹스 (공감형, 손실회피형, 가격실수형, 실구매자썰형)

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

# ==========================================
# 2. 카테고리별 4대 후킹 스타일 믹스 라이브러리
# (공감형, 손실회피형, 가격실수형, 실구매자썰형)
# ==========================================
SHORT_HOOKS = {
    'SHOES': [
        "조금만 오래 걸어도 발바닥 아프고 피로 쉽게 쌓이는 사람 손? 👟",
        "제발 브랜드 운동화 정가 10만원씩 다 주고 사지 마세요 🫢",
        "이 스펙 신발이 이 가격에 풀린 건 담당자 실수 아닌가... 👀",
        "발 편한 데일리 전투화 찾다가 이건 진짜 줍줍각이라 공유함 👟"
    ],
    'DIGITAL_TECH': [
        "게임할 때 선 걸리적거리고 충전 깜빡해서 꺼진 적 다들 있지? 🎧",
        "비싼 게이밍 장비 거품가 다 주고 사면 진짜 아까움 ⚡",
        "충전독까지 주는 구성인데 이 가격이면 가격 잘못 올린 듯 🫢",
        "비싼 브랜드 헤드셋 쓰다가 이거 스펙 보고 현타 왔음... 🎧"
    ],
    'KIDS': [
        "애들은 금방 쑥쑥 커서 옷 제값 다 주고 사면 제일 아까움 👶",
        "우리 아이 편하게 입힐 데일리 등원룩/외출복 찾는다면 🍼",
        "놀이터용 막 입히는 옷 찾다가 가성비 미쳐서 바로 담음 🧸",
        "브랜드 키즈 의류가 보세 옷보다 싸게 풀린 거 실화인가 👀"
    ],
    'LIVING': [
        "어차피 매달 쓰는 건데 마트 가서 제값 다 주면 제일 속 쓰린 생필품 🧻",
        "집에 떨어지면 불안해서 박스로 쟁여둬야 마음 편한 필수템 📦",
        "단가 계산기 두드려봤더니 마트/다이소 반값도 안 나옴 🧼",
        "생필품은 핫딜 떴을 때 박스 단위로 사두는 게 진짜 돈 버는 거임 ✨"
    ],
    'FOOD_PROCESSED': [
        "퇴근하고 밥 차리기 귀찮을 때 배달비 아끼는 치트키 🍜",
        "배달앱 켤 때마다 2~3만원씩 깨지는데 이럴 때 냉동실 채워둬야 함 🥟",
        "출출할 때 바로 꺼내먹는 야식용 비상식량 최저가 떴길래 공유함 😋",
        "개당 단가 계산해봤더니 편의점 1+1보다 훨씬 싸네요 🔥"
    ],
    'FOOD_FRESH': [
        "요즘 장바구니 물가 무서운데 마트 반값 수준으로 풀린 먹거리 🛒",
        "외식 한 번 참는 가격으로 온 가족 배부르게 먹는 꿀템 🥩",
        "고기/과일 정육점 가격 보고 망설였는데 산지직송급 특가 발견 😋",
        "후기 검증된 신선 먹거리 역대급 단가 떴으니 마트 가지 마세요 🍎"
    ],
    'BEVERAGE_SNACK': [
        "매일 마시는 커피·음료 편의점 가격 아까웠던 사람? ☕",
        "물·음료 떨어질 때마다 무겁게 들고 오지 말고 박스로 쟁여둘 타이밍 🧊",
        "탕비실/냉장고 채워둘 음료 단가 계산해보고 바로 긁었음 🧃",
        "한 캔/한 병에 이 가격이면 편의점 반값도 안 되는 수준 🔥"
    ],
    'BEAUTY': [
        "환절기만 되면 피부 땅기고 건조해서 고민인 사람? 🧴",
        "올영 세일 때도 이 가격은 안 나왔으니 정가 주지 마세요 💄",
        "공병 몇 개째 비우는 인생템인데 최저가 떴길래 공유함 ✨",
        "피부과/올영 상위권인 그 제품 역대급 혜택가 뜸 🌸"
    ],
    'HOME_APPLIANCE': [
        "퇴근 후 집안일 시간 확 줄여주는 삶의 질 상승 가전 🏠",
        "대기업 비싼 가전 살 필요 없이 실속형으로 뽕 뽑는 템 ⚡",
        "이 가격에 이 기능이면 진작 살 걸 그랬음... 가성비 종결 🔥"
    ],
    'FASHION': [
        "옷장은 꽉 찼는데 매번 입을 옷 없어서 고민인 사람? 👕",
        "백화점 브랜드 옷 정가 다 주고 사면 바보 되는 이유 👀",
        "어디에나 편하게 받쳐 입을 가성비 기본템 찾다가 발견함 ✨"
    ],
    'GENERAL': [
        "살까 말까 고민하면서 장바구니에만 넣어뒀던 분들 주목 👀",
        "제발 제값 다 주고 사지 마세요! 실시간 최저가 떴습니다 🔥",
        "담당자가 할인 쿠폰 중복 적용 풀어둔 듯... 실시간 품절 각 ⚡"
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
    
    # 1. 신발 (최우선 매칭)
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['SHOES']):
        return 'SHOES'
        
    # 2. 디지털 / 게이밍 기기
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['DIGITAL_TECH']):
        return 'DIGITAL_TECH'
        
    # 3. 생활 / 주방가전
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['HOME_APPLIANCE']):
        return 'HOME_APPLIANCE'
        
    # 4. 뷰티 / 화장품
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['BEAUTY']):
        return 'BEAUTY'
        
    # 5. 키즈 / 육아
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['KIDS']):
        return 'KIDS'
        
    # 6. 생활 / 위생용품 (세제, 화장지 등)
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['LIVING']):
        return 'LIVING'
        
    # 7. 가공식품 / 만두 / 간편식 / 밀키트
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['FOOD_PROCESSED']):
        return 'FOOD_PROCESSED'
        
    # 8. 신선식품 / 정육 / 수산 / 과일
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['FOOD_FRESH']):
        return 'FOOD_FRESH'
        
    # 9. 음료 / 간식 / 커피
    if any(kw in clean_text for kw in CATEGORY_KEYWORDS['BEVERAGE_SNACK']):
        return 'BEVERAGE_SNACK'
        
    # 10. 의류 / 패션
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

def get_short_hook(category: str) -> str:
    """카테고리에 맞는 4대 스타일 믹스 후킹 무작위 추출"""
    hooks = SHORT_HOOKS.get(category, SHORT_HOOKS['GENERAL'])
    return random.choice(hooks)

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

def format_threads_post(title: str, product_link: str) -> tuple[str, str]:
    """
    쇼츠/스레드 초압축 3단 포맷터:
    1) 상황/공감/손실회피/가격실수/실구매자썰 믹스 후킹 (1줄)
    2) 물품 소개 + 가격 (1줄)
    3) 구매 링크 안내 (1줄)
    """
    clean_name = clean_title_for_display(title)
    category = classify_deal_category(title)
    hook = get_short_hook(category)
    price, qty, unit = parse_price_and_quantity(title)
    
    product_line = build_product_price_line(clean_name, price, qty, unit)
    
    root_lines = [
        hook,
        product_line,
        "",
        "🔗 구매 좌표는 첫 번째 댓글에 남겨둘게! 👇"
    ]
    root_content = "\n".join(root_lines)
    
    reply_lines = [
        f"👉 구매 좌표 바로가기:\n{product_link}",
        "",
        "※ 파트너스 활동의 일환으로 수수료를 제공받을 수 있습니다."
    ]
    reply_content = "\n".join(reply_lines)
    
    return root_content, reply_content

def format_post(title: str, product_link: str) -> str:
    """텔레그램 알림용 포맷터"""
    clean_name = clean_title_for_display(title)
    category = classify_deal_category(title)
    hook = get_short_hook(category)
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
