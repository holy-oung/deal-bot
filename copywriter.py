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
# 2. 트렌드 취미 및 라이프스타일 연계 초압축 후킹 생성기
# ==========================================
def get_trendy_hook(title: str, category: str) -> str:
    """상품 세부 품목과 2030 트렌드 취미(러닝, 배그 사플, 오운완, 땀냄새 빨래 등)를 정밀 결합한 1줄 후킹"""
    t = title.lower()
    
    # 1. 신발 / 러닝 / 트레킹 / 아웃도어
    if category == 'SHOES':
        if any(k in t for k in ['러닝화', '런닝화', '러닝', '런닝', '운동화', '스니커즈']):
            options = [
                "요즘 러닝 많이 뛰는데 일반 운동화 신고 뛰는 사람 손? 🏃",
                "러닝 크루 들어가려고 가성비 런닝화 찾고 있었다면 👟",
                "발 편한 데일리 러닝화 찾다가 이건 진짜 줍줍각이라 공유함 👟",
                "제발 브랜드 러닝화 정가 10만원씩 다 주고 사지 마세요 🫢"
            ]
        elif any(k in t for k in ['트레킹화', '등산화', '고어텍스']):
            options = [
                "요즘 날씨 좋아서 주말마다 등산·트레킹 가시는 분들 🥾",
                "가볍고 발목 탄탄하게 잡아주는 트레킹화 찾는다면 🏔️",
                "고어텍스 트레킹화가 이 가격에 풀린 건 담당자 실수 아닌가... 👀",
                "조금만 오래 걸어도 발바닥 아프고 피로 쉽게 쌓이는 사람 손? 👟"
            ]
        else:
            options = [
                "출퇴근할 때 매일 편하게 막 신을 데일리 슈즈 찾는다면 👟",
                "제발 브랜드 신발 정가 다 주고 사지 마세요 🫢",
                "조금만 걸어도 발바닥 아프고 피로 쉽게 쌓이는 사람 손? 👟"
            ]
        return random.choice(options)
        
    # 2. 디지털 / 게이밍 (배그/발로란트 사플, 데스크테리어)
    if category == 'DIGITAL_TECH':
        if any(k in t for k in ['헤드셋', '이어폰', '헤드폰', '독거미', '게이밍']):
            options = [
                "요즘 배그나 발로란트 할 때 사플 안 돼서 답답했던 사람? 🎧",
                "게임할 때 선 걸리적거리고 충전 깜빡해서 꺼진 적 다들 있지? 🎧",
                "충전독까지 주는 무선 헤드셋인데 이 가격이면 담당자 실수인 듯 🫢",
                "비싼 브랜드 헤드셋 쓰다가 이거 스펙 보고 현타 왔음... 🎧"
            ]
        elif any(k in t for k in ['키보드', '마우스', '모니터', '거치대']):
            options = [
                "책상 위 지저분한 선 정리하고 감성 데스크테리어 맞출 타이밍 ⚡",
                "게임 장비 욕심 있는 분들 지금 역대급 가성비 떴습니다 💻",
                "장시간 PC 작업할 때 손목 피로했던 사람 손? ⌨️"
            ]
        else:
            options = [
                "비싼 전자기기 거품가 다 주고 사면 진짜 아까움 ⚡",
                "책상 위 복잡한 충전선 때문에 스트레스 받는 사람 손? ⚡",
                "가성비 끝판왕 IT 장비 찾고 있었다면 💻"
            ]
        return random.choice(options)
        
    # 3. 생활용품 / 세제 (러닝 땀냄새, 자취 살림)
    if category == 'LIVING':
        if any(k in t for k in ['세제', '섬유유연제', '피죤', '다우니', '퍼실', '리큐', '테크']):
            options = [
                "요즘 러닝·헬스하느라 땀 많이 날 텐데 땀냄새 싹 지우려면 이거 써야 함 🧼",
                "빨래 꿉꿉한 냄새 한 방에 잡는 대용량 섬유유연제 역대급 단가 떴음 🧺",
                "어차피 매달 쓰는 건데 마트 가서 제값 다 주면 제일 속 쓰린 생필품 🧻",
                "단가 계산기 두드려봤더니 마트/다이소 반값도 안 나옴 🧼"
            ]
        elif any(k in t for k in ['휴지', '화장지', '물티슈', '롤휴지']):
            options = [
                "집에 떨어지면 불안해서 박스로 쟁여둬야 마음 편한 필수템 📦",
                "자취생 필수템! 마트에서 무겁게 들고 오지 말고 문 앞 배송으로 쟁여둘 타이밍 🧻",
                "생필품은 핫딜 떴을 때 박스 단위로 사두는 게 진짜 돈 버는 거임 ✨"
            ]
        else:
            options = [
                "어차피 매달 쓰는 건데 마트 가서 제값 다 주면 제일 속 쓰린 생필품 🧻",
                "집에 떨어지면 불안해서 박스로 쟁여둬야 마음 편한 필수템 📦",
                "단가 계산기 두드려봤더니 마트/다이소 반값도 안 나옴 🧼"
            ]
        return random.choice(options)
        
    # 4. 식품 / 간편식 (오운완 식단, 넷플릭스 야식, 밥 차리기 귀찮을 때)
    if category in ('FOOD_PROCESSED', 'FOOD_FRESH'):
        if any(k in t for k in ['닭가슴살', '프로틴', '단백질', '소고기', '한우', '삼겹살']):
            options = [
                "운동하는 사람 손!! 식단 나랑 같이하자 💪",
                "오운완 후 단백질 채워둘 식단 비상식량 최저가 떴음 🍗",
                "외식 한 번 참는 가격으로 고기 배 터지게 먹는 꿀템 🥩",
                "닭가슴살 물려서 식단 고민이었다면 지금이 쟁여둘 타이밍 😋"
            ]
        elif any(k in t for k in ['만두', '교자', '피자', '치킨', '너겟', '라면', '대창', '곱창', '전골']):
            options = [
                "퇴근하고 밥 차리기 귀찮을 때 배달비 아끼는 치트키 🍜",
                "주말에 넷플릭스 보면서 맥주 한잔 곁들일 꿀맛 안주 찾는다면 🍺",
                "배달앱 켤 때마다 2~3만원씩 깨지는데 이럴 때 냉동실 채워둬야 함 🥟",
                "출출할 때 바로 꺼내먹는 야식용 비상식량 최저가 떴길래 공유함 😋"
            ]
        elif any(k in t for k in ['과일', '귤', '감귤', '사과', '복숭아']):
            options = [
                "요즘 장바구니 과일 물가 살벌한데 마트 반값 수준으로 풀림 🍎",
                "집에서 상큼하게 비타민 충전할 제철 과일 산지직송급 특가 🍊",
                "마트 가면 과일 하나 집기도 겁나는데 역대급 단가 떴음 🛒"
            ]
        else:
            options = [
                "요즘 장바구니 물가 무서운데 마트 반값 수준으로 풀린 먹거리 🛒",
                "퇴근하고 밥 차리기 귀찮을 때 배달비 아끼는 치트키 🍜",
                "냉동실에 쟁여두면 출출할 때 든든한 야식/반찬 비상식량 🥟"
            ]
        return random.choice(options)
        
    # 5. 음료 / 커피 / 간식 (오운완 제로음료, 홈카페)
    if category == 'BEVERAGE_SNACK':
        if any(k in t for k in ['제로', '탄산수', '음료', '콜라', '사이다']):
            options = [
                "운동 끝나고 시원하게 마실 제로 음료 박스로 채워둘 타이밍 🧊",
                "한 캔에 이 가격이면 편의점 반값도 안 되는 수준 🔥",
                "물·음료 떨어질 때마다 무겁게 들고 오지 말고 문 앞 배송으로 쟁여두자 🧃"
            ]
        elif any(k in t for k in ['커피', '원두', '캡슐', '카누', '아메리카노']):
            options = [
                "하루 커피 2잔씩 마시는데 매달 커피값 10만원씩 깨지는 사람? ☕",
                "홈카페 차려두고 출근길 텀블러에 타서 커피값 굳힐 타이밍 ☕",
                "매일 마시는 커피 편의점/카페 가격 아까웠다면 무조건 확인 ☕"
            ]
        else:
            options = [
                "매일 마시는 커피·음료 편의점 가격 아까웠던 사람? ☕",
                "물·음료 떨어질 때마다 무겁게 들고 오지 말고 박스로 쟁여둘 타이밍 🧊",
                "탕비실/냉장고 채워둘 음료 단가 계산해보고 바로 긁었음 🧃"
            ]
        return random.choice(options)
        
    # 6. 뷰티 (야외 러닝 자외선/피부 진정, 올영 랭킹)
    if category == 'BEAUTY':
        options = [
            "야외 러닝이나 운동하고 자외선에 지친 피부 진정시킬 타이밍 🧴",
            "올영 세일 때도 이 가격은 안 나왔으니 정가 주지 마세요 💄",
            "환절기만 되면 피부 땅기고 건조해서 고민인 사람 손? 🧴",
            "공병 몇 개째 비우는 인생템인데 최저가 떴길래 공유함 ✨"
        ]
        return random.choice(options)
        
    # 7. 키즈 / 육아
    if category == 'KIDS':
        options = [
            "애들은 금방 쑥쑥 커서 옷 제값 다 주고 사면 제일 아까움 👶",
            "우리 아이 편하게 입힐 데일리 등원룩/외출복 찾는다면 🍼",
            "놀이터용 막 입히는 옷 찾다가 가성비 미쳐서 바로 담음 🧸",
            "브랜드 키즈 의류가 보세 옷보다 싸게 풀린 거 실화인가 👀"
        ]
        return random.choice(options)
        
    # 8. 가전 / 패션 / 일반
    if category == 'HOME_APPLIANCE':
        options = [
            "퇴근 후 집안일 시간 확 줄여주는 삶의 질 상승 가전 🏠",
            "대기업 비싼 가전 살 필요 없이 실속형으로 뽕 뽑는 템 ⚡",
            "이 가격에 이 기능이면 진작 살 걸 그랬음... 가성비 종결 🔥"
        ]
        return random.choice(options)
        
    if category == 'FASHION':
        options = [
            "요즘 유행하는 고프코어/러닝용으로 편하게 입을 기본템 찾는다면 👕",
            "옷장은 꽉 찼는데 매번 입을 옷 없어서 고민인 사람? 👕",
            "백화점 브랜드 옷 정가 다 주고 사면 바보 되는 이유 👀"
        ]
        return random.choice(options)
        
    options = [
        "살까 말까 고민하면서 장바구니에만 넣어뒀던 분들 주목 👀",
        "제발 제값 다 주고 사지 마세요! 실시간 최저가 떴습니다 🔥",
        "담당자가 할인 쿠폰 중복 적용 풀어둔 듯... 실시간 품절 각 ⚡"
    ]
    return random.choice(options)

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
    1) 트렌드 취미/라이프스타일 연계 공감 후킹 (1줄)
    2) 물품 소개 + 가격 (1줄)
    3) 구매 링크 안내 (1줄)
    """
    clean_name = clean_title_for_display(title)
    category = classify_deal_category(title)
    hook = get_trendy_hook(title, category)
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
