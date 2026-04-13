# ============================================================
#  kakao_token_generator.py  |  카카오 토큰 최초 발급 + .env 자동 저장
#
#  사용법:
#  1. python kakao_token_generator.py 실행
#  2. 브라우저에서 카카오 로그인
#  3. 리디렉션된 URL의 ?code= 값 복사 후 터미널에 붙여넣기
#  4. Access Token / Refresh Token 이 .env 에 자동 저장됨
# ============================================================
import requests
import webbrowser
from config import KAKAO_REST_API_KEY, update_env

REDIRECT_URI = "https://example.com/oauth"  # 카카오 앱 설정의 Redirect URI 와 동일하게


def step1_get_code() -> str:
    auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
    )
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("▶ 브라우저가 열리면 카카오 로그인 후")
    print("  리디렉션된 URL 전체를 복사하세요.")
    print(f"\n  직접 열기: {auth_url}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    webbrowser.open(auth_url)

    redirected = input("리디렉션된 URL 전체(또는 code= 값만) 붙여넣기: ").strip()

    # URL 전체를 붙여넣은 경우 code 값만 추출
    if "code=" in redirected:
        code = redirected.split("code=")[-1].split("&")[0]
    else:
        code = redirected
    return code


def step2_get_token(code: str):
    resp = requests.post("https://kauth.kakao.com/oauth/token", data={
        "grant_type":   "authorization_code",
        "client_id":    KAKAO_REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code":         code,
    })
    data = resp.json()

    access_token  = data.get("access_token", "")
    refresh_token = data.get("refresh_token", "")

    if not access_token:
        print(f"❌ 토큰 발급 실패: {data}")
        return

    # .env 파일에 자동 저장
    update_env("KAKAO_ACCESS_TOKEN",  access_token)
    update_env("KAKAO_REFRESH_TOKEN", refresh_token)

    print("\n✅ 토큰 발급 성공! .env 파일에 자동 저장되었습니다.")
    print(f"   Access Token  : {access_token[:20]}...")
    print(f"   Refresh Token : {refresh_token[:20]}...")
    print("\n이제 python main.py 를 실행하면 됩니다. 🎉")


if __name__ == "__main__":
    code = step1_get_code()
    step2_get_token(code)
