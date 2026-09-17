# link_helper.py
# 상품명 정제 및 최적의 제품 링크 추출 모듈
# 방안: 토스 쉐어링크 100% 전용 모드

import re
import urllib.parse
from toss_api import toss_api

def is_toss_deal(direct_url: str = "", title: str = "") -> bool:
    """해당 핫딜이 토스 상품인지 판별"""
    if direct_url and ('toss.im' in direct_url.lower() or 'toss.com' in direct_url.lower()):
        return True
    if title:
        title_lower = title.lower()
        if '[토스]' in title_lower or '토스' in title_lower:
            return True
    return False

def clean_product_keyword(raw_title: str) -> str:
    """게시글 제목에서 쇼핑몰명, 가격, 배송비 등 불필요한 태그를 제거하고 핵심 검색어 추출"""
    text = raw_title
    text = re.sub(r'\[.*?\]', ' ', text)
    text = re.sub(r'\(.*?\)', ' ', text)
    text = re.sub(r'\b\d+[\d,]*\s*원?\b', ' ', text)
    text = re.sub(r'(?:무료배송|무배|유료|배송비|우주패스|카드할인|쿠폰적용|체감가|역대가|끌올)', ' ', text)
    text = re.sub(r'[\/_,\+~!\?@#\$%\^&\*\(\)\[\]\{\}\<\>|:;]+', ' ', text)
    words = [w.strip() for w in text.split() if w.strip()]
    if len(words) > 4:
        words = words[:4]
    keyword = ' '.join(words).strip()
    return keyword if keyword else raw_title[:30].strip()

def is_coupang_deal(direct_url: str = "", title: str = "") -> bool:
    if direct_url and ('coupang.com' in direct_url.lower()):
        return True
    if title and ('[쿠팡]' in title or '쿠팡' in title):
        return True
    return False

def get_product_link(direct_url: str, title: str) -> str:
    """
    최적의 제품 링크 반환:
    1. 토스 링크 -> 토스 쉐어링크 API 발급
    2. 쿠팡 링크 -> 쿠팡 파트너스 UI 봇을 통한 링크 발급
    """
    if not direct_url:
        return title
        
    if is_toss_deal(direct_url, title):
        # 토스 쉐어링크 API 호출
        sharelink = toss_api.create_sharelink(direct_url, title)
        return sharelink
        
    if is_coupang_deal(direct_url, title):
        # 쿠팡 UI 브라우저 봇을 통한 단축 링크 생성
        from coupang_ui import generate_coupang_link_via_ui
        keyword = clean_product_keyword(title)
        short_link = generate_coupang_link_via_ui(keyword, headless=False)
        return short_link if short_link else direct_url
        
    return direct_url

