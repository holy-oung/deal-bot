# scraper.py
# 핫딜 커뮤니티(뽐뿌) 크롤링 모듈

import base64
import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.google.com/'
}

# 쿠팡 파트너스 수익화가 불가능한 비실물/금융/통신 키워드 블랙리스트
NON_MONETIZABLE_KEYWORDS = [
    # 통신 / 알뜰폰 / 요금제
    '알뜰폰', '요금제', '유심', 'esim', '통신사', '번호이동', '기기변경', '회선', '데이터무제한',
    'sk7모바일', 'ktm모바일', 'u+알뜰', '헬로모바일', '아이즈모바일', '시월모바일', '모빙',
    '이지모바일', '티플러스', '프리티', '에르엘', '여유텔레콤', '인스모바일', '선불유심',
    
    # 상품권 / 머니 / 포인트 / 페이 / 캐시
    '상품권', '해피머니', '컬쳐랜드', '도서문화상품권', '기프티콘', 'e쿠폰', '이쿠폰', '금액권',
    '네이버페이', '토스포인트', '엘포인트', '머니트리', '캐시', '포인트', '적립', '페이백',
    '온누리상품권', '문화상품권', '구글기프트', '구글플레이',
    
    # 금융 / 렌탈 / 부동산 / 단순 이벤트
    '렌탈', '청약', '대출', '적금', '예금', '카드발급', '청구할인', '출석체크', '출첵', '퀴즈', '설문', '응모'
]

NON_MONETIZABLE_DOMAINS = [
    'siwolmobile.com', 'eyes.co.kr', 'tplusmobile.me', 'freet.co.kr', 'mobing.co.kr',
    'uplussave.com', 'ktmmobile.com', 'sk7mobile.com', 'insmobile.co.kr', 'yeoyou.co.kr',
    'eyagi.co.kr', 'annextele.com', 'smartelmobile.com'
]

def is_monetizable_deal(title: str, url: str = "") -> tuple[bool, str]:
    """쿠팡 파트너스로 수익화가 가능한 실물 쇼핑 딜인지 검증"""
    title_lower = title.lower()
    for kw in NON_MONETIZABLE_KEYWORDS:
        if kw in title_lower:
            return False, f"비수익 품목 키워드 감지 ({kw})"
            
    url_lower = url.lower()
    for dom in NON_MONETIZABLE_DOMAINS:
        if dom in url_lower:
            return False, f"비수익 도메인 감지 ({dom})"
            
    return True, "수익화 가능"

def decode_ppomppu_target(redirect_url: str) -> str:
    """뽐뿌 리다이렉트 링크 내부의 base64 타겟 주소 디코딩"""
    try:
        parsed = urllib.parse.urlparse(redirect_url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'target' in params:
            encoded = params['target'][0]
            missing_padding = len(encoded) % 4
            if missing_padding:
                encoded += '=' * (4 - missing_padding)
            return base64.b64decode(encoded).decode('utf-8', errors='ignore')
    except Exception:
        pass
    return redirect_url

def is_low_res_image(url: str | None) -> bool:
    """초저화질 썸네일(뽐뿌 목록 썸네일, 작은 아이콘 등) 여부 판정"""
    if not url:
        return True
    url_lower = url.lower()
    low_res_keywords = ['_thumb', 'small_', '/thumb/', 'icon', 'logo', 'banner']
    return any(kw in url_lower for kw in low_res_keywords)

def fetch_deal_details(ppom_url: str) -> dict:
    """
    듀얼 트랙(Agent Reach 원문 맥락 + Research 1차 출처) 정보 수집 & 고해상도 이미지 선별:
    1) 원문 쇼핑몰 링크 추출
    2) 트랙 1 (원문/소셜 맥락): td.han 본문 텍스트 및 900px 원본 이미지 추출
    3) 트랙 2 (1차 출처 쇼핑몰): 공식 OpenGraph og:image 추출
    4) 해상도 선별기(Resolution Comparator): 고화질(쇼핑몰 og:image 또는 900w 원본) 채택, 불가 시 None(텍스트 모드)
    """
    direct_url = ppom_url
    community_text = ""
    community_high_res = None
    mall_high_res = None
    
    try:
        res = requests.get(ppom_url, headers=HEADERS, timeout=5)
        res.encoding = 'cp949'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 뽐뿌 상단 구매 링크 탐색
        for a in soup.select('a'):
            href = a.get('href', '')
            if 's.ppomppu.co.kr' in href:
                direct_url = decode_ppomppu_target(href)
                break
                
        # 2. 트랙 1: 작성자 원문 본문 텍스트 & 고화질 업로드 이미지 (td.han)
        han = soup.select_one('td.han')
        if han:
            community_text = han.get_text(separator=' ', strip=True)
            for img in han.find_all('img'):
                src = img.get('src', '')
                if src.startswith('//'):
                    src = 'https:' + src
                if '900w_' in src or ('data' in src and not is_low_res_image(src)):
                    community_high_res = src
                    break
    except Exception as e:
        print(f"[Warning] 상세 링크 추출 실패 ({ppom_url}): {e}")

    # 3. 트랙 2: 1차 출처 쇼핑몰 메타데이터 파싱 (Research)
    if direct_url and direct_url.startswith('http') and direct_url != ppom_url:
        try:
            m_res = requests.get(direct_url, headers=HEADERS, timeout=4, allow_redirects=True)
            m_soup = BeautifulSoup(m_res.text, 'html.parser')
            og_img = m_soup.select_one('meta[property="og:image"]')
            if og_img and og_img.get('content'):
                candidate = og_img.get('content')
                if candidate.startswith('//'):
                    candidate = 'https:' + candidate
                if not is_low_res_image(candidate):
                    mall_high_res = candidate
        except Exception:
            pass

    # 4. 해상도 선별기 (Resolution Comparator)
    # 쇼핑몰 공식 고화질 og:image 우선 -> 원문 900w 원본 차선 -> 둘 다 없으면 None(텍스트 모드)
    final_image = None
    selection_reason = ""
    if mall_high_res and not is_low_res_image(mall_high_res):
        final_image = mall_high_res
        selection_reason = "1차 출처 쇼핑몰 공식 고화질 og:image 채택"
    elif community_high_res and not is_low_res_image(community_high_res):
        final_image = community_high_res
        selection_reason = "원문 본문 900px 고화질 원본 이미지 채택"
    else:
        final_image = None
        selection_reason = "고화질 검증 실패로 저화질 방지용 순수 텍스트(TEXT) 모드 채택"

    return {
        'direct_url': direct_url,
        'context_text': community_text,
        'high_res_image': final_image,
        'image_reason': selection_reason
    }

def fetch_direct_product_link(ppom_url: str) -> str:
    """하위 호환성을 위한 단독 원문 링크 추출 함수"""
    details = fetch_deal_details(ppom_url)
    return details['direct_url']

def fetch_latest_deals() -> list:
    """뽐뿌 뽐뿌게시판에서 최신 핫딜 목록 추출"""
    url = 'https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu'
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        res.encoding = 'cp949'
    except Exception as e:
        print(f"[Error] 뽐뿌 접속 실패: {e}")
        return []
        
    soup = BeautifulSoup(res.text, 'html.parser')
    deals = []
    
    rows = soup.select('tr.baseList')
    for r in rows:
        title_el = r.select_one('a.baseList-title')
        if not title_el:
            continue
            
        title = title_el.text.strip()
        href = title_el.get('href', '')
        if not href.startswith('http'):
            href = 'https://www.ppomppu.co.kr/zboard/' + href
            
        # 게시글 고유 ID (no)
        parsed_url = urllib.parse.urlparse(href)
        deal_id = urllib.parse.parse_qs(parsed_url.query).get('no', [''])[0]
        if not deal_id:
            continue
            
        # 썸네일 이미지
        thumb = r.select_one('.baseList-thumb img')
        thumb_url = thumb.get('src') if thumb else None
        if thumb_url and thumb_url.startswith('//'):
            thumb_url = 'https:' + thumb_url
            
        deals.append({
            'id': deal_id,
            'title': title,
            'ppom_url': href,
            'thumb_url': thumb_url
        })
        
    return deals
