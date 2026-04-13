#!/usr/bin/env python3
# ============================================================
#  main.py  |  날씨 기반 코디 자동화 — 메인 실행 파일
#
#  실행: python main.py
#  cron: 0 6 * * * /usr/bin/python3 /path/to/outfit_automation/main.py
# ============================================================
import sys
import traceback
from datetime import datetime

from weather       import get_weather, weather_to_outfit_keywords
from outfit_ai     import generate_outfit
from image_search  import get_daily_images
from html_generator import generate_html
from kakao_notify  import send_kakao_message


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def main():
    log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    log("👗 오늘의 코디 자동화 시작")
    log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 1. 날씨 수집
    log("1️⃣  날씨 데이터 수집 중...")
    try:
        weather  = get_weather()
        keywords = weather_to_outfit_keywords(weather)
        log(f"   → {weather['temp']}°C, {weather['description']}, 강수 {weather['rain_prob']}%")
    except Exception as e:
        log(f"❌ 날씨 수집 실패: {e}")
        traceback.print_exc()
        sys.exit(1)

    # 2. OpenAI API 코디 생성
    log("2️⃣  AI 코디 생성 중 (OpenAI)...")
    try:
        outfit = generate_outfit(weather, keywords)
        log(f"   → 무드: {outfit.get('mood', '?')} | 팔레트: {outfit.get('color_palette', '?')}")
    except Exception as e:
        log(f"❌ AI 코디 생성 실패: {e}")
        traceback.print_exc()
        sys.exit(1)

    # 3. 이미지 검색 (Unsplash 키 있으면 우선)
    log("3️⃣  패션 이미지 검색 중...")
    try:
        images = get_daily_images(keywords["season"], outfit)
        src = images.get("image_source", "naver")
        m_cnt = len(images.get("male_images", []))
        f_cnt = len(images.get("female_images", []))
        log(f"   → {src} · 남성 {m_cnt}장, 여성 {f_cnt}장")
    except Exception as e:
        log(f"⚠️  이미지 검색 실패 (이미지 없이 진행): {e}")
        images = {"male_images": [], "female_images": []}

    # 4. HTML 파일 생성
    log("4️⃣  HTML 파일 생성 중...")
    try:
        html_path = generate_html(weather, keywords, outfit, images)
        log(f"   → 저장됨: {html_path}")
    except Exception as e:
        log(f"❌ HTML 생성 실패: {e}")
        traceback.print_exc()
        sys.exit(1)

    # 5. 카카오톡 알림
    log("5️⃣  카카오톡 알림 전송 중...")
    try:
        send_kakao_message(weather, outfit, keywords, html_path)
    except Exception as e:
        log(f"⚠️  카카오톡 전송 실패 (HTML은 정상 저장됨): {e}")

    log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    log("✅ 완료! outfit_today.html 을 열어 확인하세요.")
    log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    main()
