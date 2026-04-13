# ============================================================
#  kakao_notify.py  |  카카오톡 나에게 보내기 + Refresh Token 자동 갱신
# ============================================================
import json
import requests
import config
from config import (
    KAKAO_REST_API_KEY,
    update_env,
)

SEND_URL    = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
REFRESH_URL = "https://kauth.kakao.com/oauth/token"


# ── 토큰 갱신 ─────────────────────────────────────────────

def refresh_access_token() -> str:
    """
    Refresh Token으로 새 Access Token 발급 후 .env 자동 저장
    - 카카오는 갱신 시 Refresh Token도 새로 내려주는 경우가 있으므로 함께 저장
    """
    refresh_token = config.KAKAO_REFRESH_TOKEN
    if not refresh_token:
        raise ValueError("KAKAO_REFRESH_TOKEN 이 .env 에 없습니다. kakao_token_generator.py 로 재발급하세요.")

    resp = requests.post(REFRESH_URL, data={
        "grant_type":    "refresh_token",
        "client_id":     KAKAO_REST_API_KEY,
        "refresh_token": refresh_token,
    })
    data = resp.json()

    if "access_token" not in data:
        raise RuntimeError(f"토큰 갱신 실패: {data}")

    new_access  = data["access_token"]
    new_refresh = data.get("refresh_token")   # 카카오가 새 refresh_token 내려줄 때만 존재

    # .env 파일 + 현재 프로세스 환경변수 동시 업데이트
    update_env("KAKAO_ACCESS_TOKEN", new_access)
    config.KAKAO_ACCESS_TOKEN = new_access
    print("🔄 Access Token 갱신 완료 → .env 저장됨")

    if new_refresh:
        update_env("KAKAO_REFRESH_TOKEN", new_refresh)
        config.KAKAO_REFRESH_TOKEN = new_refresh
        print("🔄 Refresh Token 도 갱신 완료 → .env 저장됨")

    return new_access


# ── 메시지 빌더 ───────────────────────────────────────────

def _build_template(weather: dict, outfit: dict, keywords: dict) -> str:
    rain_line = f"\n{keywords['rain_tip']}" if keywords["rain_tip"] else ""
    text = (
        f"👗 오늘의 코디 알림\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🌤 날씨: {weather['description']} {weather['temp']}°C\n"
        f"   (체감 {weather['feels_like']}°C · 습도 {weather['humidity']}%){rain_line}\n\n"
        f"🎨 오늘의 무드: {outfit.get('mood', '데일리 룩')}\n"
        f"   팔레트: {outfit.get('color_palette', '')}\n\n"
        f"👔 남성 코디\n"
        f"   상의: {outfit['male'].get('top','')}\n"
        f"   하의: {outfit['male'].get('bottom','')}\n"
        f"   아우터: {outfit['male'].get('outer','없음')}\n\n"
        f"👗 여성 코디\n"
        f"   상의: {outfit['female'].get('top','')}\n"
        f"   하의: {outfit['female'].get('bottom','')}\n"
        f"   아우터: {outfit['female'].get('outer','없음')}\n\n"
        f"📄 상세보기 → outfit_today.html"
    )
    return json.dumps({
        "object_type":  "text",
        "text":         text,
        "link":         {"web_url": "", "mobile_web_url": ""},
        "button_title": "상세 코디 보기",
    }, ensure_ascii=False)


# ── 실제 전송 (1회 시도) ──────────────────────────────────

def _do_send(access_token: str, template: str) -> requests.Response:
    return requests.post(
        SEND_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
        data={"template_object": template},
    )


# ── 메인 발송 함수 ────────────────────────────────────────

def send_kakao_message(weather: dict, outfit: dict, keywords: dict, html_path: str) -> bool:
    """
    카카오톡 '나에게 보내기' 전송
    - 401(토큰 만료) 응답 시 Refresh Token으로 자동 갱신 후 1회 재시도
    - 갱신된 토큰은 .env 파일에 자동 저장
    """
    template     = _build_template(weather, outfit, keywords)
    access_token = config.KAKAO_ACCESS_TOKEN

    resp = _do_send(access_token, template)

    # ── 토큰 만료 → 자동 갱신 후 재시도 ──────────────────
    if resp.status_code == 401:
        print("⚠️  Access Token 만료 → 자동 갱신 시도...")
        try:
            access_token = refresh_access_token()
            resp = _do_send(access_token, template)   # 재시도
        except Exception as e:
            print(f"❌ 토큰 갱신 실패: {e}")
            print("   → kakao_token_generator.py 로 수동 재발급이 필요합니다.")
            return False

    # ── 결과 확인 ─────────────────────────────────────────
    if resp.status_code == 200 and resp.json().get("result_code") == 0:
        print("✅ 카카오톡 전송 성공")
        return True
    else:
        print(f"❌ 카카오톡 전송 실패: {resp.status_code} {resp.text}")
        return False
