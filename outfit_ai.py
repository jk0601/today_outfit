# ============================================================
#  outfit_ai.py  |  OpenAI API → 남녀 코디 텍스트 생성
# ============================================================
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


def _thickness_directive(layer_temp: int) -> str:
    """기온 구간별로 모델이 두꺼운 옷을 임의로 넣지 않도록 명시"""
    if layer_temp >= 28:
        return (
            "매우 더움: 패딩·두꺼운 코트·울 두께 니트·목도리·장갑 추천 금지. "
            "외투(outer)는 비어 있거나 '없음'에 가깝게. 반팔·린넨·쇼츠 수준 필수."
        )
    if layer_temp >= 23:
        return (
            "더움: 패딩·롱패딩·두꺼운 울코트·목도리 금지. "
            "가벼운 가디건·얇은 셔츠 정도만. 반팔+얇은 겉옷 조합 허용."
        )
    if layer_temp >= 17:
        return (
            "온화: 긴팔·가디건·아주 얇은 자켓 수준. 패딩·두꺼운 코트 금지."
        )
    if layer_temp >= 12:
        return (
            "선선함: 니트·트렌치·가벼운 자켓까지 허용. 패딩·극두께 니트는 피할 것."
        )
    if layer_temp >= 5:
        return "쌀쌀~추움: 코트·두꺼운 니트·방풍 아우터까지 허용."
    return "추움: 패딩·방한 아우터·레이어링 적극 허용."


def generate_outfit(weather: dict, keywords: dict) -> dict:
    """OpenAI API에 날씨 정보를 넘겨 남녀 코디를 JSON 형태로 받아옴"""

    client = OpenAI(api_key=OPENAI_API_KEY)
    lt = int(keywords.get("layer_temp", round((weather["temp"] + weather["feels_like"]) / 2)))

    prompt = f"""
당신은 기상 수치와 **동일한 두께**의 옷만 추천하는 스타일리스트입니다. 기온을 무시하고 겨울 아이템을 넣으면 안 됩니다.

오늘 서울의 날씨 정보입니다:
- 기온: {weather['temp']}°C (체감 {weather['feels_like']}°C)
- **코디 두께 기준 환산 온도(실제와 체감의 평균 반올림)**: 약 **{lt}°C**
- 날씨: {weather['description']}
- 강수확률: {weather['rain_prob']}%
- 습도: {weather['humidity']}%
- 시즌 느낌: {keywords['season']}
- 추천 레이어링: {keywords['layer_keywords']}

**두께 규칙 (반드시 준수, 남녀 모두 적용)**:
{_thickness_directive(lt)}

JSON의 outer/top/bottom/shoes/accessory 필드에는 위 규칙을 벗어나는 두께를 쓰지 마세요.

아래 JSON 형식으로만 응답해 주세요. 코드블록(```) 없이 순수 JSON만 출력하세요.

{{
  "male": {{
    "outer": "아우터 추천 (없으면 빈 문자열)",
    "top": "상의 추천",
    "bottom": "하의 추천",
    "shoes": "신발 추천",
    "accessory": "소품/포인트 아이템",
    "tip": "한 줄 스타일링 팁"
  }},
  "female": {{
    "outer": "아우터 추천 (없으면 빈 문자열)",
    "top": "상의 추천",
    "bottom": "하의 추천",
    "shoes": "신발 추천",
    "accessory": "소품/포인트 아이템",
    "tip": "한 줄 스타일링 팁"
  }},
  "color_palette": "오늘 날씨에 어울리는 컬러 3가지 (예: 카멜, 베이지, 다크브라운)",
  "mood": "오늘 코디 무드 한 단어 (예: 캐주얼 시크)"
}}
"""

    msg = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    import json
    raw = (msg.choices[0].message.content or "").strip()
    # 혹시 코드블록이 포함된 경우 제거
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


if __name__ == "__main__":
    from weather import weather_to_outfit_keywords

    w = {"temp": 26, "feels_like": 28, "humidity": 60, "description": "맑음", "rain_prob": 0}
    k = weather_to_outfit_keywords(w)
    result = generate_outfit(w, k)
    import json; print(json.dumps(result, ensure_ascii=False, indent=2))
