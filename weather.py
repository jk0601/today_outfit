# ============================================================
#  weather.py  |  날씨 데이터 수집 및 코디 키워드 변환
# ============================================================
import requests
from config import OPENWEATHER_API_KEY, CITY


def get_weather() -> dict:
    """OpenWeatherMap에서 서울 날씨를 가져와 딕셔너리로 반환"""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": CITY,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "kr",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    temp      = round(data["main"]["temp"])
    feels     = round(data["main"]["feels_like"])
    humidity  = data["main"]["humidity"]
    desc      = data["weather"][0]["description"]
    icon_code = data["weather"][0]["icon"]
    icon_url  = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    rain_prob = 0  # 현재 날씨 API에는 강수확률 없음 → forecast로 보완

    # 1시간 예보로 강수확률 보완
    try:
        f_url = "https://api.openweathermap.org/data/2.5/forecast"
        f_resp = requests.get(f_url, params={**params, "cnt": 2}, timeout=10)
        f_data = f_resp.json()
        rain_prob = int(f_data["list"][0].get("pop", 0) * 100)
    except Exception:
        pass

    return {
        "temp": temp,
        "feels_like": feels,
        "humidity": humidity,
        "description": desc,
        "icon_url": icon_url,
        "rain_prob": rain_prob,
    }


def weather_to_outfit_keywords(w: dict) -> dict:
    """날씨 수치 → 코디 키워드 및 조언 문자열 생성

    레이어링 구간은 실제 기온과 체감의 평균으로 잡아, 더 덥게/춥게 느껴질 때
    코디 두께가 어긋나는 것을 줄입니다.
    """
    temp = w["temp"]
    feels = w["feels_like"]
    rain = w["rain_prob"]

    # 코디 두께 판단용 (체감을 반영; 정수로 반올림)
    layer_temp = round((temp + feels) / 2)

    # 기온별 레이어링 키워드 (layer_temp 기준)
    if layer_temp >= 28:
        layer = "민소매·반팔·린넨·쇼츠"
        season = "한여름"
    elif layer_temp >= 23:
        layer = "반팔·얇은 블라우스·면 팬츠"
        season = "초여름"
    elif layer_temp >= 17:
        layer = "긴팔·가디건·얇은 겉옷"
        season = "봄가을"
    elif layer_temp >= 12:
        layer = "니트·가벼운 자켓·트렌치"
        season = "선선한 봄가을"
    elif layer_temp >= 5:
        layer = "두꺼운 니트·코트·머플러"
        season = "초겨울"
    else:
        layer = "패딩·롱코트·핫팩·두꺼운 레이어링"
        season = "한겨울"

    # 비 여부
    rain_tip = ""
    if rain >= 60:
        rain_tip = "☔ 우산 필수! 방수 소재 아우터 추천"
    elif rain >= 30:
        rain_tip = "🌂 우산 챙기세요 (강수확률 {}%)".format(rain)

    return {
        "season": season,
        "layer_keywords": layer,
        "rain_tip": rain_tip,
        "layer_temp": layer_temp,  # AI·로그용 (코디 두께 기준 온도)
    }


if __name__ == "__main__":
    w = get_weather()
    print(w)
    print(weather_to_outfit_keywords(w))
