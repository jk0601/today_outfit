# ============================================================
#  html_generator.py  |  오늘의 코디 HTML 파일 생성
# ============================================================
import os
from datetime import datetime
from config import HTML_FILE, OUTPUT_DIR


def generate_html(weather: dict, keywords: dict, outfit: dict, images: dict) -> str:
    """모든 데이터를 조합해 세련된 HTML 파일을 생성하고 경로를 반환"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    img_credit = (
        "Unsplash"
        if images.get("image_source") == "unsplash"
        else "Naver Search"
    )

    today = datetime.now().strftime("%Y년 %m월 %d일")
    weekday = ["월", "화", "수", "목", "금", "토", "일"][datetime.now().weekday()]
    rain_tip_html = f'<div class="rain-tip">{keywords["rain_tip"]}</div>' if keywords["rain_tip"] else ""

    def img_cards(img_list: list) -> str:
        if not img_list:
            return '<p class="no-img">이미지를 불러올 수 없습니다.</p>'
        cards = ""
        for img in img_list:
            cards += f'''
            <a href="{img["link"]}" target="_blank" class="img-card">
              <img src="{img["thumbnail"]}" alt="{img["title"]}" loading="lazy" onerror="this.style.display='none'"/>
              <span>{img["title"][:20]}</span>
            </a>'''
        return cards

    def outfit_rows(gender_data: dict) -> str:
        rows = ""
        labels = {"outer": "아우터", "top": "상의", "bottom": "하의", "shoes": "신발", "accessory": "소품"}
        icons  = {"outer": "🧥", "top": "👕", "bottom": "👖", "shoes": "👟", "accessory": "✨"}
        for key, label in labels.items():
            val = gender_data.get(key, "")
            if val:
                rows += f'<div class="row"><span class="icon">{icons[key]}</span><span class="label">{label}</span><span class="val">{val}</span></div>'
        return rows

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>오늘의 코디 — {today}</title>
<link href="https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@300;400;500;700&family=Noto+Serif+KR:wght@500;600&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg: #faf7f4;
    --card: #ffffff;
    --text: #1a1a1a;
    --muted: #888;
    --accent: #d4a574;
    --accent2: #6e8fc9;
    --border: #ebe6df;
    --male: #e8f0fb;
    --female: #fbeaf0;
    --male-accent: #3a6abf;
    --female-accent: #bf3a6a;
    /* 밝은 헤더 */
    --header-fg: #3d3430;
    --header-date: #c76b5c;
    --header-stripe: rgba(190, 130, 110, .09);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Noto Sans KR', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 0 0 60px;
  }}

  /* ── Header (화사한 톤 + 빗금 유지) ── */
  .header {{
    color: var(--header-fg);
    padding: 32px 24px 28px;
    text-align: center;
    position: relative;
    overflow: hidden;
    background: linear-gradient(
      125deg,
      #fff9f4 0%,
      #fff0eb 28%,
      #ffe8f2 55%,
      #f3ecff 85%,
      #eef6ff 100%
    );
  }}
  .header::before {{
    content: '';
    position: absolute; inset: 0;
    background: repeating-linear-gradient(
      45deg, transparent, transparent 40px,
      var(--header-stripe) 40px, var(--header-stripe) 80px
    );
    pointer-events: none;
  }}
  .date-tag {{
    font-size: 11px; font-weight: 500; letter-spacing: 3px;
    color: var(--header-date); text-transform: uppercase; margin-bottom: 10px;
    position: relative; z-index: 1;
  }}
  .header h1 {{
    font-family: 'Jua', 'Noto Sans KR', sans-serif;
    font-size: clamp(30px, 7vw, 46px);
    font-weight: 400;
    line-height: 1.2;
    letter-spacing: -0.03em;
    font-feature-settings: "kern" 1;
    color: var(--header-fg);
    text-shadow: 0 1px 0 rgba(255,255,255,.85), 0 6px 28px rgba(255, 160, 140, .22);
    margin-bottom: 6px;
    position: relative; z-index: 1;
  }}
  .mood-badge {{
    display: inline-block;
    position: relative; z-index: 1;
    background: linear-gradient(135deg, #f0a080, #e07d6a);
    color: #fff;
    font-size: 12px; font-weight: 600;
    padding: 5px 16px; border-radius: 20px;
    letter-spacing: 0.5px; margin-top: 8px;
    box-shadow: 0 4px 16px rgba(224, 125, 106, .35);
  }}

  /* ── Weather Card ── */
  .container {{ max-width: 760px; margin: 0 auto; padding: 0 16px; }}
  .weather-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    display: flex; align-items: center; gap: 16px;
    margin-top: -20px; position: relative; z-index: 2;
    box-shadow: 0 4px 24px rgba(0,0,0,.06);
  }}
  .weather-icon img {{ width: 64px; height: 64px; }}
  .weather-info {{ flex: 1; }}
  .temp-main {{ font-size: 36px; font-weight: 700; line-height: 1; }}
  .temp-main span {{ font-size: 14px; font-weight: 400; color: var(--muted); margin-left: 4px; }}
  .weather-desc {{ font-size: 14px; color: var(--muted); margin-top: 4px; }}
  .weather-meta {{
    display: flex; gap: 16px; margin-top: 10px;
    font-size: 12px; color: var(--muted);
  }}
  .weather-meta b {{ color: var(--text); font-weight: 500; }}
  .rain-tip {{
    background: #fff8e1; border-left: 3px solid #f5c518;
    border-radius: 8px; padding: 10px 14px;
    font-size: 13px; font-weight: 500; color: #7a5f00;
    margin-top: 12px;
  }}

  /* ── Color Palette ── */
  .palette-section {{
    margin-top: 24px;
    display: flex; align-items: center; gap: 12px;
  }}
  .palette-label {{ font-size: 12px; color: var(--muted); font-weight: 500; letter-spacing: 1px; }}
  .palette-text {{ font-size: 13px; font-weight: 500; color: var(--accent); }}

  /* ── Gender Sections ── */
  .section-title {{
    font-size: 13px; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: var(--muted);
    margin: 32px 0 12px;
  }}
  .gender-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,.04);
  }}
  .gender-header {{
    padding: 16px 20px 12px;
    display: flex; align-items: center; gap: 10px;
  }}
  .gender-header.male  {{ background: var(--male);   border-bottom: 1px solid #cfddf8; }}
  .gender-header.female{{ background: var(--female); border-bottom: 1px solid #f8cfdf; }}
  .gender-emoji {{ font-size: 22px; }}
  .gender-title {{ font-size: 16px; font-weight: 700; }}
  .gender-title.male   {{ color: var(--male-accent); }}
  .gender-title.female {{ color: var(--female-accent); }}

  .outfit-rows {{ padding: 14px 20px; }}
  .row {{
    display: flex; align-items: center; gap: 10px;
    padding: 9px 0; border-bottom: 1px solid var(--border);
    font-size: 14px;
  }}
  .row:last-child {{ border-bottom: none; }}
  .icon {{ font-size: 16px; width: 22px; text-align: center; }}
  .label {{ color: var(--muted); width: 44px; font-size: 12px; flex-shrink: 0; }}
  .val {{ flex: 1; font-weight: 500; }}
  .tip-box {{
    margin: 0 20px 16px;
    background: var(--bg); border-radius: 10px;
    padding: 10px 14px; font-size: 13px; color: var(--muted);
    border-left: 3px solid var(--accent);
  }}
  .tip-box.female {{ border-left-color: var(--female-accent); }}

  /* ── Image Gallery ── */
  .img-gallery {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
    padding: 16px 20px;
    border-top: 1px solid var(--border);
  }}
  .img-card {{
    display: flex; flex-direction: column; gap: 6px;
    text-decoration: none; color: var(--text);
    border-radius: 10px; overflow: hidden;
    border: 1px solid var(--border);
    transition: transform .18s, box-shadow .18s;
  }}
  .img-card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,.1); }}
  .img-card img {{
    width: 100%; aspect-ratio: 3/4; object-fit: cover;
    background: var(--bg);
  }}
  .img-card span {{
    font-size: 11px; color: var(--muted);
    padding: 4px 8px 8px; line-height: 1.3;
  }}
  .no-img {{ color: var(--muted); font-size: 13px; padding: 16px 20px; }}

  /* ── Footer ── */
  .footer {{
    text-align: center; margin-top: 40px;
    font-size: 11px; color: var(--muted); letter-spacing: 1px;
  }}

  @media (max-width: 480px) {{
    .weather-card {{ flex-direction: column; text-align: center; }}
    .weather-meta {{ justify-content: center; }}
    .img-gallery {{ grid-template-columns: repeat(2, 1fr); }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="date-tag">{today} ({weekday}요일)</div>
  <h1>오늘의 코디</h1>
  <div class="mood-badge">{outfit.get('mood', '데일리 룩')}</div>
</div>

<div class="container">

  <!-- 날씨 카드 -->
  <div class="weather-card">
    <div class="weather-icon">
      <img src="{weather['icon_url']}" alt="날씨 아이콘"/>
    </div>
    <div class="weather-info">
      <div class="temp-main">{weather['temp']}°C<span>체감 {weather['feels_like']}°C</span></div>
      <div class="weather-desc">{weather['description']}</div>
      <div class="weather-meta">
        <span>💧 습도 <b>{weather['humidity']}%</b></span>
        <span>☔ 강수 <b>{weather['rain_prob']}%</b></span>
      </div>
    </div>
  </div>
  {rain_tip_html}

  <!-- 컬러 팔레트 -->
  <div class="palette-section">
    <span class="palette-label">Today's Palette</span>
    <span class="palette-text">🎨 {outfit.get('color_palette', '')}</span>
  </div>

  <!-- 남성 코디 -->
  <div class="section-title">Men's Outfit</div>
  <div class="gender-card">
    <div class="gender-header male">
      <span class="gender-emoji">👔</span>
      <span class="gender-title male">남성 코디</span>
    </div>
    <div class="outfit-rows">
      {outfit_rows(outfit['male'])}
    </div>
    <div class="tip-box">{outfit['male'].get('tip', '')}</div>
    <div class="img-gallery">
      {img_cards(images.get('male_images', []))}
    </div>
  </div>

  <!-- 여성 코디 -->
  <div class="section-title">Women's Outfit</div>
  <div class="gender-card">
    <div class="gender-header female">
      <span class="gender-emoji">👗</span>
      <span class="gender-title female">여성 코디</span>
    </div>
    <div class="outfit-rows">
      {outfit_rows(outfit['female'])}
    </div>
    <div class="tip-box female">{outfit['female'].get('tip', '')}</div>
    <div class="img-gallery">
      {img_cards(images.get('female_images', []))}
    </div>
  </div>

  <div class="footer">자동 생성 · Powered by OpenWeatherMap + OpenAI + {img_credit}</div>
</div>

</body>
</html>"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    return HTML_FILE
