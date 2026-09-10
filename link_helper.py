# link_helper.py
# 상품명 정제 및 최적의 제품 링크 추출 모듈

import re
import urllib.parse
from config import COUPANG_AF_ID

def clean_product_keyword(raw_title: str) -> str:
    """게시글 제목에서 쇼핑몰명, 가격, 배송비 등 불필요한 태그를 제거하고 핵심 검색어 추출"""
    text = raw_title
    # 대괄호 [쇼핑몰/혜택], 소괄호 (가격/배송비) 제거
    text = re.sub(r'\[.*?\]', ' ', text)
    text = re.sub(r'\(.*?\)', ' ', text)
    
    # 가격 표기 및 배송비 단어 제거 (예: 17,900원, 무배, 무료배송, 역대가 등)
    text = re.sub(r'\b\d+[\d,]*\s*원\b', ' ', text)
    text = re.sub(r'(?:무료배송|무배|유료|배송비|우주패스|카드할인|쿠폰적용|체감가|역대가|끌올)', ' ', text)
    
    # 특수문자 정리
    text = re.sub(r'[\/_,\+~!\?@#\$%\^&\*\(\)\[\]\{\}\<\>|:;]+', ' ', text)
    
    words = [w.strip() for w in text.split() if w.strip()]
    
    # 검색 정확도를 위해 최대 4~5단어로 제한
    if len(words) > 4:
        words = words[:4]
        
    keyword = ' '.join(words).strip()
    return keyword if keyword else raw_title[:30].strip()

def make_coupang_search_url(keyword: str) -> str:
    """쿠팡 검색 결과에 파트너스 AF코드 태그 삽입"""
    encoded = urllib.parse.quote(keyword)
    return f"https://www.coupang.com/np/search?q={encoded}&channel=user&lptag={COUPANG_AF_ID}"

def get_product_link(direct_url: str, title: str) -> str:
    """
    모든 링크를 100% 쿠팡 파트너스 수익 링크로 결정:
    1. 쿠팡 상품인 경우: 본인 AF태그가 삽입된 쿠팡 다이렉트 링크 반환
    2. 타 쇼핑몰(11번가, G마켓, 네이버 등)인 경우: 해당 제품의 쿠팡 최저가 검색 파트너스 링크로 강제 전환
    """
    if direct_url and 'coupang.com' in direct_url:
        # 기존 다른 lptag 파라미터가 있다면 제거 후 본인 파트너스 태그 삽입
        clean_url = re.sub(r'[?&]lptag=[^&]*', '', direct_url)
        separator = '&' if '?' in clean_url else '?'
        return f"{clean_url}{separator}lptag={COUPANG_AF_ID}"
        
    # 비(非)쿠팡 핫딜은 100% 쿠팡 파트너스 검색 링크로 전환
    keyword = clean_product_keyword(title)
    return make_coupang_search_url(keyword)
