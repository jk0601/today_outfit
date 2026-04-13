# ============================================================
#  image_search.py  |  Unsplash 검색 (우선) + Naver 폴백
# ============================================================
import html as html_lib
import requests

from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, UNSPLASH_ACCESS_KEY

UNSPLASH_API = "https://api.unsplash.com"
# 링크에 붙이는 UTM (Unsplash API 가이드라인)
_UNSPLASH_UTM = "utm_source=weather_outfit_automation&utm_medium=referral"


def _with_utm(page_url: str) -> str:
    if not page_url:
        return page_url
    sep = "&" if "?" in page_url else "?"
    return f"{page_url}{sep}{_UNSPLASH_UTM}"

# 날씨 시즌(한글) → Unsplash 검색용 영어 힌트
_SEASON_EN = {
    "한여름": "summer street style",
    "초여름": "spring summer casual",
    "봄가을": "transitional outfit",
    "선선한 봄가을": "autumn layered look",
    "초겨울": "winter coat outfit",
    "한겨울": "winter cold weather style",
}


def _season_hint(season_ko: str) -> str:
    return _SEASON_EN.get(season_ko, "fashion outfit")


def _unsplash_headers() -> dict:
    return {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY.strip()}"}


def _unsplash_trigger_download(photo_id: str) -> None:
    """Unsplash 가이드라인: 사용한 사진에 대해 다운로드 트래킹 요청"""
    try:
        requests.get(
            f"{UNSPLASH_API}/photos/{photo_id}/download",
            headers=_unsplash_headers(),
            timeout=5,
        )
    except Exception:
        pass


def search_unsplash(query: str, count: int = 3) -> list[dict]:
    """
    Unsplash Search API → html_generator 호환 형식
    [{"title", "link", "thumbnail"}, ...]
    """
    q = " ".join(query.split())[:160]
    if not q.strip():
        q = "fashion outfit"

    resp = requests.get(
        f"{UNSPLASH_API}/search/photos",
        headers=_unsplash_headers(),
        params={
            "query": q,
            "per_page": min(count, 30),
            "orientation": "portrait",
            "content_filter": "high",
        },
        timeout=15,
    )
    resp.raise_for_status()
    results = []
    for photo in resp.json().get("results", [])[:count]:
        pid = photo.get("id", "")
        urls = photo.get("urls") or {}
        links = photo.get("links") or {}
        user = photo.get("user") or {}
        name = user.get("name", "Photographer")
        thumb = urls.get("regular") or urls.get("small") or urls.get("thumb", "")
        page = _with_utm(links.get("html", "https://unsplash.com"))
        alt = photo.get("description") or photo.get("alt_description") or "Outfit inspiration"
        title = f"{name} · Unsplash — {alt}"
        title = html_lib.escape(title[:200])
        results.append({
            "title": title,
            "link": page,
            "thumbnail": thumb,
            "_unsplash_id": pid,
        })

    for item in results:
        pid = item.pop("_unsplash_id", "")
        if pid:
            _unsplash_trigger_download(pid)

    return results


def search_outfit_images_naver(query: str, count: int = 3) -> list[dict]:
    """
    Naver 이미지 검색 API로 패션 이미지 URL 목록 반환
    반환 형식: [{"title": ..., "link": ..., "thumbnail": ...}, ...]
    """
    url = "https://openapi.naver.com/v1/search/image"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {
        "query": query,
        "display": count,
        "sort": "sim",
        "filter": "large",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])

    results = []
    for item in items:
        raw_title = item.get("title", "").replace("<b>", "").replace("</b>", "")
        results.append({
            "title": html_lib.escape(raw_title[:200]),
            "link": item.get("link", ""),
            "thumbnail": item.get("thumbnail", ""),
        })
    return results


def search_outfit_images(query: str, count: int = 3) -> list[dict]:
    """설정에 따라 Unsplash 또는 Naver로 검색"""
    if UNSPLASH_ACCESS_KEY.strip():
        return search_unsplash(query, count=count)
    return search_outfit_images_naver(query, count=count)


def _build_unsplash_queries(season: str, outfit: dict) -> tuple[str, str]:
    hint = _season_hint(season)
    m = outfit.get("male") or {}
    f = outfit.get("female") or {}
    male_q = (
        f"mens fashion outfit {hint} "
        f"{m.get('outer', '')} {m.get('top', '')} {m.get('bottom', '')} {m.get('shoes', '')}"
    )
    female_q = (
        f"womens fashion outfit {hint} "
        f"{f.get('outer', '')} {f.get('top', '')} {f.get('bottom', '')} {f.get('shoes', '')}"
    )
    return male_q, female_q


def _build_naver_queries(season: str, outfit: dict) -> tuple[str, str]:
    m = outfit.get("male") or {}
    f = outfit.get("female") or {}
    male_q = f"{season} 남성 코디 {m.get('top', '')} {m.get('bottom', '')}"
    female_q = f"{season} 여성 코디 {f.get('top', '')} {f.get('bottom', '')}"
    return male_q, female_q


def get_daily_images(weather_keywords: str, outfit: dict) -> dict:
    """남성/여성 각각 코디 이미지 3장씩 검색 (Unsplash 키 있으면 우선)"""
    season = weather_keywords
    count = 3

    if UNSPLASH_ACCESS_KEY.strip():
        mq, fq = _build_unsplash_queries(season, outfit)
        try:
            return {
                "male_images": search_unsplash(mq, count=count),
                "female_images": search_unsplash(fq, count=count),
                "image_source": "unsplash",
            }
        except Exception:
            if NAVER_CLIENT_ID and NAVER_CLIENT_SECRET:
                mq, fq = _build_naver_queries(season, outfit)
                return {
                    "male_images": search_outfit_images_naver(mq, count=count),
                    "female_images": search_outfit_images_naver(fq, count=count),
                    "image_source": "naver",
                }
            raise

    mq, fq = _build_naver_queries(season, outfit)
    return {
        "male_images": search_outfit_images_naver(mq, count=count),
        "female_images": search_outfit_images_naver(fq, count=count),
        "image_source": "naver",
    }


if __name__ == "__main__":
    if UNSPLASH_ACCESS_KEY.strip():
        imgs = search_unsplash("mens minimalist winter outfit lookbook", count=3)
    else:
        imgs = search_outfit_images_naver("봄 남성 트렌치코트 코디", count=3)
    for i in imgs:
        print(i)
