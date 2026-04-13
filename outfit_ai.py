# ============================================================
#  outfit_ai.py  |  OpenAI API → 남녀 코디 텍스트 생성
# ============================================================
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


def generate_outfit(weather: dict, keywords: dict) -> dict:
    """OpenAI API에 날씨 정보를 넘겨 남녀 코디를 JSON 형태로 받아옴"""

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
오늘 서울의 날씨 정보입니다:
- 기온: {weather['temp']}°C (체감 {weather['feels_like']}°C)
- 날씨: {weather['description']}
- 강수확률: {weather['rain_prob']}%
- 습도: {weather['humidity']}%
- 시즌 느낌: {keywords['season']}
- 추천 레이어링: {keywords['layer_keywords']}

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
    # 테스트용 더미 데이터
    w = {"temp": 12, "feels_like": 9, "humidity": 70, "description": "흐림", "rain_prob": 40}
    k = {"season": "선선한 봄가을", "layer_keywords": "니트·자켓·트렌치코트", "rain_tip": "우산 챙기세요"}
    result = generate_outfit(w, k)
    import json; print(json.dumps(result, ensure_ascii=False, indent=2))
