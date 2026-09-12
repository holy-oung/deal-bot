# threads_poster.py
# Meta 공식 Threads Graph API 기반 자동 포스팅 모듈
# '딸깍 Threads 공장 Community Edition v1.11.7' 규격 적용

import time
import requests
from config import THREADS_ACCESS_TOKEN, THREADS_USER_ID, ENABLE_THREADS_POSTING

GRAPH_API_BASE = "https://graph.threads.net/v1.0"

def is_threads_configured() -> bool:
    """스레드 API 연동 정보가 설정되어 있는지 확인"""
    return bool(THREADS_ACCESS_TOKEN and THREADS_USER_ID and ENABLE_THREADS_POSTING)

def validate_threads_credentials() -> dict:
    """Threads Access Token 및 사용자 ID 유효성 검증"""
    if not THREADS_ACCESS_TOKEN or not THREADS_USER_ID:
        return {"valid": False, "error": "THREADS_ACCESS_TOKEN 또는 THREADS_USER_ID가 설정되지 않았습니다."}
        
    url = f"{GRAPH_API_BASE}/{THREADS_USER_ID}"
    params = {
        "fields": "id,username",
        "access_token": THREADS_ACCESS_TOKEN
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if res.status_code == 200 and "id" in data:
            return {"valid": True, "username": data.get("username"), "userId": data.get("id")}
        return {"valid": False, "error": data.get("error", {}).get("message", f"HTTP {res.status_code}")}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def _wait_for_container_ready(creation_id: str, max_wait: int = 15) -> bool:
    """컨테이너 상태가 FINISHED가 될 때까지 대기 (최대 max_wait초)"""
    url = f"{GRAPH_API_BASE}/{creation_id}"
    params = {
        "fields": "status,error_message",
        "access_token": THREADS_ACCESS_TOKEN
    }
    start = time.time()
    while time.time() - start < max_wait:
        try:
            res = requests.get(url, params=params, timeout=5)
            data = res.json()
            status = data.get("status")
            if status == "FINISHED":
                return True
            elif status == "ERROR":
                print(f"    [Threads Container Error] {data.get('error_message')}")
                return False
        except Exception:
            pass
        time.sleep(2)
    return True

def _create_container(text: str, image_url: str = None, reply_to_id: str = None) -> str | None:
    """미디어 또는 텍스트 컨테이너 생성 (1단계)"""
    url = f"{GRAPH_API_BASE}/{THREADS_USER_ID}/threads"
    payload = {
        "access_token": THREADS_ACCESS_TOKEN,
    }
    
    # 이미지 지원: 공개 HTTPS 주소이며 저화질(small_, _thumb 등)이 아닌 경우에만 이미지 발행
    is_valid_image = bool(image_url and image_url.startswith("https://"))
    if is_valid_image:
        low_res_markers = ['_thumb', 'small_', '/thumb/', 'icon', 'logo']
        if any(m in image_url.lower() for m in low_res_markers):
            is_valid_image = False
            
    if is_valid_image:
        payload["media_type"] = "IMAGE"
        payload["image_url"] = image_url
        if text:
            payload["text"] = text
    else:
        payload["media_type"] = "TEXT"
        payload["text"] = text
        
    if reply_to_id:
        payload["reply_to_id"] = reply_to_id
        
    try:
        res = requests.post(url, data=payload, timeout=20)
        data = res.json()
        if res.status_code == 200 and "id" in data:
            return data["id"]
        print(f"    [Threads Error] 컨테이너 생성 실패: {data.get('error', {}).get('message', res.text)}")
    except Exception as e:
        print(f"    [Threads Exception] 컨테이너 요청 오류: {e}")
    return None

def _publish_container(creation_id: str) -> str | None:
    """생성된 컨테이너 실제 발행 (3단계)"""
    url = f"{GRAPH_API_BASE}/{THREADS_USER_ID}/threads_publish"
    payload = {
        "creation_id": creation_id,
        "access_token": THREADS_ACCESS_TOKEN
    }
    try:
        res = requests.post(url, data=payload, timeout=20)
        data = res.json()
        if res.status_code == 200 and "id" in data:
            return data["id"]
        print(f"    [Threads Error] 게시물 발행 실패: {data.get('error', {}).get('message', res.text)}")
    except Exception as e:
        print(f"    [Threads Exception] 발행 요청 오류: {e}")
    return None

def post_to_threads(root_text: str, reply_text: str = None, image_url: str = None) -> dict:
    """
    스레드(Threads) 2단 분리 자동 포스팅:
    1) 본문 (Root Post): 추천 피드 노출을 위해 링크 없이 발행
    2) 첫 댓글 (Reply Post): 구매 링크 및 파트너스 문구 발행 (재시도 및 인덱싱 대기 보강)
    """
    if not is_threads_configured():
        # 토큰 미설정 시 안전한 Dry-run 안내
        print("    ℹ️ [Threads] 토큰 미설정 상태 (Dry-run 모의 발행 성공 처리)")
        print(f"       [미리보기 본문] {root_text.splitlines()[0]}...")
        if reply_text:
            print(f"       [미리보기 댓글] {reply_text.splitlines()[0]}...")
        return {"success": True, "dry_run": True, "root_id": "dry_run_root_id"}

    mode_str = f"고화질 이미지 모드 ({image_url[:55]}...)" if image_url and not any(m in image_url.lower() for m in ['_thumb', 'small_']) else "클린 텍스트 모드 (저화질 방지 & 가독성 극대화)"
    print(f"    🧵 [Threads] 공식 API 본문 게시 중... [{mode_str}]")
    
    # 1. 본문 컨테이너 생성
    root_creation_id = _create_container(text=root_text, image_url=image_url)
    if not root_creation_id:
        return {"success": False, "error": "본문 컨테이너 생성 실패"}
        
    # 2. 컨테이너 준비 대기
    _wait_for_container_ready(root_creation_id, max_wait=10 if image_url else 5)
    
    # 3. 본문 발행
    root_post_id = _publish_container(root_creation_id)
    if not root_post_id:
        return {"success": False, "error": "본문 발행 실패"}
        
    print(f"    -> [Threads] 본문 발행 성공! (Post ID: {root_post_id})")
    
    # 4. 첫 번째 댓글(답글)로 구매 링크 발행 (재시도 로직으로 누락 원천 차단)
    if reply_text:
        time.sleep(3.5)  # 본문 서버 인덱싱 대기 (최소 3.5초)
        print("    🧵 [Threads] 첫 번째 답글(구매 링크) 작성 중...")
        
        reply_creation_id = None
        for attempt in range(1, 4):
            reply_creation_id = _create_container(text=reply_text, reply_to_id=root_post_id)
            if reply_creation_id:
                break
            print(f"       [재시도 {attempt}/3] 본문 인덱싱 대기 후 답글 재시도...")
            time.sleep(3)
            
        if reply_creation_id:
            _wait_for_container_ready(reply_creation_id, max_wait=6)
            reply_post_id = None
            for p_attempt in range(1, 3):
                reply_post_id = _publish_container(reply_creation_id)
                if reply_post_id:
                    break
                time.sleep(2)
                
            if reply_post_id:
                print(f"    -> [Threads] 구매 링크 답글 발행 성공! (Reply ID: {reply_post_id})")
            else:
                print("    -> [Threads Warning] 구매 링크 답글 발행 실패 (본문은 정상 게시됨)")
        else:
            print("    -> [Threads Warning] 구매 링크 답글 컨테이너 생성 실패")

    return {"success": True, "root_id": root_post_id}
