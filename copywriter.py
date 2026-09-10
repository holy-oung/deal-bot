# copywriter.py
# 쓰레드 감성의 친근한 대화체 + 동품목 경쟁제품 비교 포맷 생성기

import re
import random

# 동품목 대표 제품들의 기준 시중가 벤치마크 데이터베이스
COMPETITOR_BENCHMARKS = [
    {
        'keywords': ['김', '도시락김'],
        'unit': '봉지',
        'competitor': '양반 도시락김',
        'comp_unit_price': 250
    },
    {
        'keywords': ['칫솔'],
        'unit': '개',
        'competitor': '오랄비 일반 칫솔',
        'comp_unit_price': 1500
    },
    {
        'keywords': ['랩', '매직랩', '크린랩'],
        'unit': '개',
        'competitor': '일반 마트 크린랩',
        'comp_unit_price': 4500
    },
    {
        'keywords': ['라면', '신라면', '진라면', '짜파게티', '너구리'],
        'unit': '봉지',
        'competitor': '편의점 신라면',
        'comp_unit_price': 1000
    },
    {
        'keywords': ['생수', '삼다수', '스파클'],
        'unit': '병',
        'competitor': '편의점 삼다수',
        'comp_unit_price': 1100
    },
    {
        'keywords': ['커피', '카누', '스틱'],
        'unit': '개',
        'competitor': '카누 마일드 스틱',
        'comp_unit_price': 230
    },
    {
        'keywords': ['물티슈'],
        'unit': '팩',
        'competitor': '다이소 100매 물티슈',
        'comp_unit_price': 1200
    },
    {
        'keywords': ['화장지', '휴지', '롤'],
        'unit': '롤',
        'competitor': '크리넥스 3겹 화장지',
        'comp_unit_price': 800
    },
    {
        'keywords': ['햇반', '오뚜기밥', '즉석밥'],
        'unit': '개',
        'competitor': '마트 CJ 햇반',
        'comp_unit_price': 1350
    },
    {
        'keywords': ['만두', '교자'],
        'unit': '봉지',
        'competitor': '비비고 왕교자',
        'comp_unit_price': 4600
    },
    {
        'keywords': ['등심', '한우', '소고기'],
        'unit': '100g',
        'competitor': '일반 정육점 1등급 한우',
        'comp_unit_price': 11000
    },
    {
        'keywords': ['치킨', '너겟', '가라아게'],
        'unit': '봉지',
        'competitor': '고메 크리스피 치킨',
        'comp_unit_price': 7900
    },
    {
        'keywords': ['세제', '액체세제'],
        'unit': 'L',
        'competitor': '퍼실 파워젤',
        'comp_unit_price': 4200
    },
    {
        'keywords': ['밀폐용기', '반찬통'],
        'unit': '개',
        'competitor': '일반 락앤락 밀폐용기',
        'comp_unit_price': 5500
    }
]

def clean_title_for_display(title: str) -> str:
    """쇼핑몰 태그 등을 깔끔하게 정리한 제품명"""
    t = re.sub(r'\[.*?\]', '', title)
    t = re.sub(r'\(.*?\)', '', t)
    return t.strip()

def parse_price_and_quantity(title: str):
    """제목에서 가격, 수량, 단위 추출"""
    price = None
    price_match = re.search(r'\(([\d,]+)\s*(?:원)?\s*\/', title)
    if price_match:
        try:
            price = int(price_match.group(1).replace(',', ''))
        except ValueError:
            price = None
            
    qty = None
    unit = None
    
    # g/kg 처리
    weight_match = re.search(r'(\d+)\s*(kg|g)', title, re.IGNORECASE)
    if weight_match and not any(k in title for k in ['개', '봉', '팩', '캔']):
        val = int(weight_match.group(1))
        unit_str = weight_match.group(2).lower()
        if unit_str == 'kg':
            val = val * 1000
        # 100g 단위로 환산
        qty = val // 100 if val >= 100 else 1
        unit = "100g"
    else:
        qty_match = re.search(r'(\d+)\s*(개|봉|매|팩|입|캔|병|박스|포|롤|세트)', title)
        if qty_match:
            try:
                qty = int(qty_match.group(1))
                unit = qty_match.group(2)
            except ValueError:
                qty = None

    return price, qty, unit

def find_competitor_info(title: str, unit: str, my_unit_price: int):
    """제목 키워드를 기반으로 경쟁/대체 제품과 기준 단가 매칭"""
    t_lower = title.lower()
    for item in COMPETITOR_BENCHMARKS:
        if any(kw in t_lower for kw in item['keywords']):
            return item['competitor'], item['comp_unit_price'], item['unit']
            
    # 매칭되는 벤치마크가 없는 일반 품목의 경우
    comp_name = "시중 비슷한 브랜드 제품"
    calc_unit = unit if unit else "개"
    comp_price = int(my_unit_price * 1.5 // 100 * 100) if my_unit_price else 0
    return comp_name, comp_price, calc_unit

def format_post(title: str, product_link: str) -> str:
    """
    사용자가 원하는 완벽한 쓰레드 대화체 포맷:
    
    편의점에서 1+1보면 못참는 사람? 하나 당 가격 계산하는 사람있어?
    이번에 엄청 할인한 상품 나왔어
    
    11,250원 ( <s>16,000원</s> 29% 할인 )
    체감가는 1봉지에 140원이야!!
    양반 도시락김은 1봉지에 250원이야!!
    
    https://...
    """
    clean_name = clean_title_for_display(title)
    price, qty, unit = parse_price_and_quantity(title)
    
    # 1. 후킹 질문 및 도입부
    hooks = [
        "편의점에서 1+1 보면 못 참는 사람? 하나당 가격 계산하는 사람 있어?\n이번에 엄청 할인한 상품 나왔어!!",
        "마트 가면 개당 얼마인지 꼭 계산해 보는 사람 손?\n이번에 진짜 역대급 단가로 풀린 거 있어!!",
        "어차피 매번 사 먹고 쓰는 건데 제값 주고 사면 아깝잖아?\n이번에 할인 제대로 들어간 거 나왔어!!"
    ]
    hook_text = random.choice(hooks)
    
    # 2. 가격 및 체감가 계산
    if price:
        # 정상가 추정 (30~45% 할인 기준 역산, 최소 500원 단위 올림)
        raw_est = price * 1.4
        estimated_original = int((raw_est + 499) // 500 * 500)
        if estimated_original <= price:
            estimated_original = price + 1000
        discount_rate = int((estimated_original - price) / estimated_original * 100)
        price_header = f"<b>{price:,}원</b> ( <s>{estimated_original:,}원</s> {discount_rate}% 할인 )"
        
        if qty and qty > 1:
            my_each = price // qty
            use_unit = unit if unit else "개"
            if use_unit == "100g":
                unit_label = "100g에"
            elif use_unit in ['봉', '봉지']:
                unit_label = "1봉지에"
            else:
                unit_label = f"1{use_unit}에"
                
            my_price_line = f"체감가는 {unit_label} <b>{my_each:,}원</b>이야!!"
            
            # 동품목 경쟁/비슷한 제품 비교
            comp_name, comp_price, comp_unit = find_competitor_info(title, use_unit, my_each)
            if comp_price > 0:
                comp_unit_label = "100g에" if comp_unit == "100g" else ("1봉지에" if comp_unit in ['봉', '봉지'] else f"1{comp_unit}에")
                comp_price_line = f"{comp_name}은 {comp_unit_label} <b>{comp_price:,}원</b>이야!!"
            else:
                comp_price_line = f"다른 브랜드는 보통 이것보다 30% 이상 비싸!!"
        else:
            my_price_line = f"<b>{clean_name}</b> 특가로 나왔어!!"
            comp_price_line = "시중에서 사려면 최소 1.5배는 더 줘야 해!!"
    else:
        price_header = f"<b>{clean_name}</b>"
        my_price_line = "지금 판매처에서 역대급 쿠폰 할인 중이야!!"
        comp_price_line = "금방 품절될 수 있으니 서두르는 게 좋아!!"

    # 3. 전체 메시지 조립
    lines = [
        hook_text,
        "",
        price_header,
        my_price_line,
        comp_price_line,
        "",
        product_link,
        "",
        "<i>※ 파트너스 활동의 일환으로 수수료를 제공받을 수 있습니다.</i>"
    ]
    
    return "\n".join(lines)

def format_threads_post(title: str, product_link: str) -> tuple[str, str]:
    """
    스레드(Threads) 알고리즘 최적화 2단 분리 포스트 포맷터:
    1) root_content (본문):
       - 외부 링크를 완전히 제외하여 알고리즘 추천 피드 노출(Reach) 극대화
       - 후킹 질문 + 가격/할인율 + 체감가 분석 + 경쟁사 비교
    2) reply_content (첫 번째 댓글):
       - 본문 바로 아래 첫 댓글로 구매 링크 및 공정위 파트너스 문구 작성
    """
    clean_name = clean_title_for_display(title)
    price, qty, unit = parse_price_and_quantity(title)
    
    # 1. 후킹 질문
    hooks = [
        "편의점에서 1+1 보면 못 참는 사람? 하나당 가격 계산하는 사람 있어? 이번에 엄청 할인한 상품 나왔어!! 🔥",
        "마트 가면 개당 얼마인지 꼭 계산해 보는 사람 손? 🙋 이번에 진짜 역대급 단가로 풀린 거 있어!!",
        "어차피 매번 사 먹고 쓰는 건데 제값 주고 사면 아깝잖아? 이번에 할인 제대로 들어간 거 나왔어!! ✨"
    ]
    hook_text = random.choice(hooks)
    
    # 2. 가격 및 체감가 (스레드는 HTML 태그를 지원하지 않으므로 깔끔한 텍스트로 구성)
    if price:
        raw_est = price * 1.4
        estimated_original = int((raw_est + 499) // 500 * 500)
        if estimated_original <= price:
            estimated_original = price + 1000
        discount_rate = int((estimated_original - price) / estimated_original * 100)
        
        price_line = f"💰 {price:,}원 (정상가 {estimated_original:,}원 대비 {discount_rate}% 할인)"
        
        if qty and qty > 1:
            my_each = price // qty
            use_unit = unit if unit else "개"
            unit_label = "100g에" if use_unit == "100g" else ("1봉지에" if use_unit in ['봉', '봉지'] else f"1{use_unit}에")
            my_price_line = f"👉 체감가는 {unit_label} {my_each:,}원이야!!"
            
            comp_name, comp_price, comp_unit = find_competitor_info(title, use_unit, my_each)
            if comp_price > 0:
                comp_unit_label = "100g에" if comp_unit == "100g" else ("1봉지에" if comp_unit in ['봉', '봉지'] else f"1{comp_unit}에")
                comp_price_line = f"⚖️ 참고로 {comp_name}은 {comp_unit_label} {comp_price:,}원이야!"
            else:
                comp_price_line = "⚖️ 다른 브랜드는 보통 이것보다 30% 이상 비싸!"
        else:
            my_price_line = f"👉 {clean_name} 역대급 특가로 나왔어!!"
            comp_price_line = "⚖️ 시중에서 사려면 최소 1.5배는 더 줘야 해!"
    else:
        price_line = f"📦 {clean_name}"
        my_price_line = "👉 지금 판매처에서 역대급 쿠폰 할인 중이야!!"
        comp_price_line = "⚖️ 금방 품절될 수 있으니 확인해 봐!"
        
    root_lines = [
        hook_text,
        "",
        price_line,
        my_price_line,
        comp_price_line,
        "",
        "🔗 구매 링크는 첫 번째 댓글에 남겨둘게! 👇"
    ]
    root_content = "\n".join(root_lines)
    
    reply_lines = [
        f"👉 특가 구매 링크 바로가기:\n{product_link}",
        "",
        "※ 파트너스 활동의 일환으로 수수료를 제공받을 수 있습니다."
    ]
    reply_content = "\n".join(reply_lines)
    
    return root_content, reply_content

