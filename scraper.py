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

def fetch_direct_product_link(ppom_url: str) -> str:
    """게시글 상세 페이지에 접속하여 실제 판매처(쇼핑몰) 원문 링크 추출"""
    try:
        res = requests.get(ppom_url, headers=HEADERS, timeout=5)
        res.encoding = 'cp949'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 뽐뿌 상단 구매 링크 탐색
        for a in soup.select('a'):
            href = a.get('href', '')
            if 's.ppomppu.co.kr' in href:
                return decode_ppomppu_target(href)
    except Exception as e:
        print(f"[Warning] 상세 링크 추출 실패 ({ppom_url}): {e}")
        
    return ppom_url

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
