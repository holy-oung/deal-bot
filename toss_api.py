import os
import time
import requests
import base64
from config import TOSS_ACCESS_KEY, TOSS_SECRET_KEY

class TossSharelinkAPI:
    def __init__(self):
        self.access_key = TOSS_ACCESS_KEY
        self.secret_key = TOSS_SECRET_KEY
        self.base_url = "https://sharelink.toss.im/openapi"
        self.auth_url = "https://oauth2.cert.toss.im/token"
        
        self.access_token = None
        self.token_expiry = 0
        
    def _get_auth_header(self):
        """Basic Auth 헤더 생성 (AccessKey:SecretKey 를 base64 인코딩)"""
        credentials = f"{self.access_key}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')
        return f"Basic {encoded_credentials}"

    def authenticate(self):
        """OAuth2 토큰 발급 및 캐싱"""
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
            
        if not self.access_key or not self.secret_key:
            print("Warning: 토스 API 키가 설정되지 않았습니다.")
            return None
            
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(self.auth_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result.get("access_token")
            expires_in = result.get("expires_in", 3600)
            
            # 여유 시간을 두고 만료 시간 설정 (10분 전 만료 처리)
            self.token_expiry = time.time() + expires_in - 600
            return self.access_token
            
        except Exception as e:
            print(f"Error: 토스 API 토큰 발급 실패 - {e}")
            return None

    def create_sharelink(self, original_url, title=""):
        """일반 쇼핑몰 링크를 토스 쉐어링크로 변환"""
        token = self.authenticate()
        if not token:
            return original_url # 토큰 발급 실패 시 원본 링크 반환
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # API 명세에 따라 url 리스트를 전송
        payload = {
            "urls": [original_url]
        }
        
        try:
            response = requests.post(f"{self.base_url}/links", headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                result = data["data"][0]
                # 성공적으로 변환되었는지 확인
                if result.get("success") and result.get("link"):
                    return result.get("link")
                
            print(f"Warning: 토스 쉐어링크 발급 실패 (응답 데이터 이상) - {data}")
            return original_url
            
        except Exception as e:
            print(f"Error: 토스 쉐어링크 API 호출 실패 - {e}")
            return original_url

    def get_best_selling(self, limit=20):
        """토스 베스트셀러 상품 조회 (추가 자동화 파이프라인용)"""
        token = self.authenticate()
        if not token:
            return []
            
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.get(f"{self.base_url}/products/best-selling", headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", {}).get("products", [])
        except Exception as e:
            print(f"Error: 토스 베스트셀러 조회 실패 - {e}")
            return []

# 싱글톤 인스턴스 생성
toss_api = TossSharelinkAPI()
