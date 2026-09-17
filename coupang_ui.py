# coupang_ui.py
# Playwright를 이용한 쿠팡 파트너스 단축 링크 자동 생성 봇

import os
from playwright.sync_api import sync_playwright

def generate_coupang_link_via_ui(keyword: str, headless: bool = False) -> str:
    """
    Playwright를 사용하여 쿠팡 파트너스 페이지에서 상품 검색 후 단축 링크를 발급합니다.
    최초 실행 시 브라우저가 열리며 쿠팡 로그인이 필요합니다.
    """
    user_data_dir = os.path.join(os.path.dirname(__file__), "playwright_user_data")
    
    with sync_playwright() as p:
        # persistent_context를 사용하여 로그인 쿠키/세션 유지
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            channel="chrome", # 로컬에 설치된 크롬 사용 권장
            args=["--disable-blink-features=AutomationControlled"], # 봇 탐지 우회
            no_viewport=True
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        try:
            print(f"🌐 [Coupang UI] 쿠팡 파트너스 링크 생성 페이지 접속 중...")
            page.goto("https://partners.coupang.com/#affiliate/ws/link", timeout=60000)
            
            # 로그인이 풀려있는지 확인 (로그인 버튼이나 아이디 입력칸이 있는지)
            if page.locator("text='로그인'").is_visible() or "/login" in page.url:
                print("⚠️ [Coupang UI] 로그인이 필요합니다. 브라우저 창에서 수동으로 로그인해주세요.")
                print("    (로그인 완료 후 봇이 자동으로 다음 단계를 진행합니다. 최대 3분 대기)")
                # 로그인이 완료되어 다시 link 페이지로 올 때까지 대기
                page.wait_for_url("**/ws/link**", timeout=180000)
                print("✅ [Coupang UI] 로그인 확인 완료!")
            
            # 검색창에 키워드 입력
            print(f"🔍 [Coupang UI] 키워드 검색: {keyword}")
            # 쿠팡 파트너스 검색창 (보통 첫 번째 textbox)
            search_box = page.get_by_role("textbox").first
            search_box.wait_for(state="visible", timeout=10000)
            search_box.fill(keyword)
            page.keyboard.press("Enter")
            
            # 검색 결과 로딩 대기
            page.wait_for_timeout(3000)
            
            # 상품에 마우스 오버 및 "링크생성" 버튼 클릭
            print(f"🖱️ [Coupang UI] '링크생성' 버튼 탐색 중...")
            # 마우스를 올려야(hover) 나타날 수도 있으므로 첫 번째 상품 이미지나 아이템 박스를 hover
            items = page.locator(".product-item, .item-list li, .search-result li") # 예측 가능한 클래스
            if items.count() > 0:
                items.first.hover()
                
            link_btn = page.get_by_text("링크 생성").first
            if not link_btn.is_visible():
                link_btn = page.locator("button", has_text="링크생성").first
                
            link_btn.wait_for(state="visible", timeout=10000)
            link_btn.click()
            
            # 링크 생성 완료 후 URL 추출
            # 보통 input 박스에 단축 URL이 들어가 있음
            page.wait_for_timeout(2000)
            print(f"📋 [Coupang UI] 단축 URL 추출 중...")
            
            # link.coupang.com/a/ 가 포함된 value를 가진 input을 찾음
            short_url_input = page.locator("input").filter(has=page.locator("xpath=.[contains(@value, 'link.coupang.com/a/')]")).first
            
            if short_url_input.is_visible():
                short_url = short_url_input.input_value()
            else:
                # 클립보드로 복사하는 버튼(URL 복사)을 누르고 클립보드 내용을 읽는 대안
                copy_btn = page.get_by_text("URL 복사").first
                copy_btn.click()
                short_url = page.evaluate("navigator.clipboard.readText()")
            
            if short_url and "link.coupang.com" in short_url:
                print(f"🎉 [Coupang UI] 발급 성공: {short_url}")
                return short_url
            else:
                print("❌ [Coupang UI] 단축 URL을 찾지 못했습니다.")
                return ""
                
        except Exception as e:
            print(f"❌ [Coupang UI] 자동화 중 오류 발생: {e}")
            return ""
        finally:
            # 상태 저장을 위해 컨텍스트 정상 종료
            browser.close()

if __name__ == "__main__":
    # 단독 테스트
    print(generate_coupang_link_via_ui("크리넥스 3겹 휴지", headless=False))
