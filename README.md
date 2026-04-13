# 👗 날씨 기반 코디 자동화 시스템

매일 오전 6시, 서울 날씨를 분석해 남녀 코디를 AI로 생성하고
HTML 파일 + 카카오톡 알림으로 받는 Python 자동화 스크립트입니다.

---

## 📁 파일 구조

```
outfit_automation/
├── .github/workflows/deploy-pages.yml  ← GitHub Actions → Pages 배포
├── scripts/ci_write_env.py             ← CI에서 Secrets → .env
├── main.py                  ← 메인 실행 (여기만 실행하면 됨)
├── config.py                ← API 키 설정 (필수 입력)
├── weather.py               ← OpenWeatherMap 날씨 수집
├── outfit_ai.py             ← OpenAI API 코디 텍스트 생성
├── image_search.py          ← Unsplash(우선) + Naver 이미지 검색
├── html_generator.py        ← HTML 파일 생성
├── kakao_notify.py          ← 카카오톡 발송
├── kakao_token_generator.py ← 카카오 토큰 최초 발급용
└── output/
    └── outfit_today.html    ← 생성된 코디 파일 (매일 덮어씀)
```

---

## 🔑 API 키 발급 방법

### 1. OpenWeatherMap (날씨)
1. https://openweathermap.org/api 가입
2. My API Keys → 키 복사
3. `config.py` → `OPENWEATHER_API_KEY` 입력
- **무료 플랜 한도**: 1분당 60회, 월 1,000,000회 → 충분

### 2. OpenAI API (코디 생성)
1. https://platform.openai.com 가입
2. API keys → Create new secret key
3. `.env` → `OPENAI_API_KEY` 입력 (선택: `OPENAI_MODEL`, 기본값 `gpt-4o-mini`)

### 3. 이미지 (Unsplash 권장)
1. https://unsplash.com/oauth/applications → **New Application** (무료)
2. 생성 후 **Access Key** 복사 → `.env`의 `UNSPLASH_ACCESS_KEY`에 붙여넣기
3. (선택) Unsplash 키가 없으면 아래 Naver로 동일하게 동작합니다.

### 3b. Naver 검색 API (이미지 폴백)
1. https://developers.naver.com → 애플리케이션 등록
2. 사용 API: **검색 (이미지)** 선택
3. Client ID / Secret → `.env` 입력
- **무료 한도**: 하루 25,000회

### 4. 카카오톡 (알림)
1. https://developers.kakao.com → 앱 생성
2. 플랫폼 → Web 추가 (사이트 도메인: https://example.com)
3. 카카오 로그인 활성화 → Redirect URI: https://example.com/oauth
4. REST API 키 → `config.py` → `KAKAO_REST_API_KEY` 입력
5. 액세스 토큰 발급:
   ```bash
   python kakao_token_generator.py
   ```
6. 발급된 토큰 → `config.py` → `KAKAO_ACCESS_TOKEN` 입력

---

## 📦 설치

```bash
pip install -r requirements.txt
```

---

## ▶ 실행

```bash
# 수동 실행
python main.py

# 개별 모듈 테스트
python weather.py
python outfit_ai.py
python image_search.py
```

---

## 🌐 GitHub Pages 자동 배포 (Actions)

저장소에 푸시한 뒤, **매일 21:00 UTC(≈ 한국 시간 다음날 06:00)**에 `main.py`가 실행되고, 생성된 `output/outfit_today.html`이 Pages에 올라갑니다. 사이트 루트(`/`)와 `/outfit_today.html` 모두 같은 페이지입니다.

### 1) Pages 설정
1. GitHub 저장소 **Settings → Pages**
2. **Build and deployment** → **Source**: **GitHub Actions** 선택

### 2) Actions Secrets 등록
**Settings → Secrets and variables → Actions**에서 다음 이름으로 등록합니다.

| Secret (필수) | 설명 |
|----------------|------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap |
| `OPENAI_API_KEY` | OpenAI |

| Secret (선택) | 설명 |
|----------------|------|
| `CITY` | 도시 (미입력 시 로컬과 동일하게 `config` 기본값) |
| `OPENAI_MODEL` | 예: `gpt-4o-mini` |
| `UNSPLASH_ACCESS_KEY` | 이미지 품질 (Unsplash) |
| `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` | Unsplash 실패 시 폴백 |
| `KAKAO_*` | 알림용 (토큰 만료 시 CI에서만 실패해도 HTML 배포는 완료됨) |

### 3) 수동 실행
**Actions** 탭 → **Deploy outfit to GitHub Pages** → **Run workflow**.

### 4) 배포 URL
- **User/Organization Pages**가 아니라 **프로젝트 Pages**인 경우: `https://<사용자>.github.io/<저장소이름>/`
- 첫 배포 후 1~2분 정도 걸릴 수 있습니다.

스케줄 시각을 바꾸려면 `.github/workflows/deploy-pages.yml`의 `cron`을 수정하세요. [crontab-guru](https://crontab.guru/)는 UTC 기준입니다.

---

## ⏰ cron 자동 스케줄 등록 (매일 오전 6시)

```bash
# crontab 편집
crontab -e

# 아래 줄 추가 (경로는 실제 경로로 수정)
0 6 * * * /usr/bin/python3 /home/사용자/outfit_automation/main.py >> /home/사용자/outfit_automation/cron.log 2>&1
```

### Windows Task Scheduler
1. 작업 스케줄러 실행
2. 작업 만들기 → 트리거: 매일 오전 06:00
3. 동작: 프로그램 → `python.exe`
4. 인수: `/path/to/outfit_automation/main.py`

---

## 🔧 커스터마이징

- **도시 변경**: `config.py` → `CITY = "Busan"` 등
- **알림 시간**: cron 표현식 변경 (`0 7 * * *` = 오전 7시)
- **이미지 수**: `image_search.py` → `count` 파라미터 조정
- **HTML 스타일**: `html_generator.py` → CSS 수정

---

## ❗ 주의사항

- 카카오 액세스 토큰은 **6시간 후 만료**됩니다.
  → 갱신 자동화가 필요하면 Refresh Token 로직 추가 필요
- API 키는 절대 GitHub에 올리지 마세요 (`.gitignore` 권장)
