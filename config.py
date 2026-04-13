# ============================================================
#  config.py  |  .env 파일에서 환경변수 로드
#  pip install python-dotenv
# ============================================================
from dotenv import load_dotenv, set_key
import os

# .env 파일 경로 고정 (어느 디렉토리에서 실행해도 동일하게 참조)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE  = os.path.join(BASE_DIR, ".env")

# .env 로드
load_dotenv(ENV_FILE)

# ── 날씨 ──────────────────────────────────────────────────
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
CITY                = os.getenv("CITY", "Seoul")

# ── OpenAI (코디 생성) ────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── 이미지 (Unsplash 우선, 키 없으면 Naver) ───────────────
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

# ── Naver 검색 (이미지 폴백) ───────────────────────────────
NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

# ── 카카오톡 ──────────────────────────────────────────────
KAKAO_REST_API_KEY  = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_ACCESS_TOKEN  = os.getenv("KAKAO_ACCESS_TOKEN", "")
KAKAO_REFRESH_TOKEN = os.getenv("KAKAO_REFRESH_TOKEN", "")

# ── 출력 경로 ─────────────────────────────────────────────
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
HTML_FILE  = os.path.join(OUTPUT_DIR, "outfit_today.html")


def update_env(key: str, value: str):
    """
    .env 파일의 특정 키 값을 업데이트하고
    현재 프로세스의 환경변수도 즉시 반영
    """
    set_key(ENV_FILE, key, value)
    os.environ[key] = value
