# CI(GitHub Actions)에서 Secrets를 .env로 기록 (값 이스케이프)
import os
from pathlib import Path

REQUIRED = ("OPENWEATHER_API_KEY", "OPENAI_API_KEY")
OPTIONAL = (
    "CITY",
    "OPENAI_MODEL",
    "UNSPLASH_ACCESS_KEY",
    "NAVER_CLIENT_ID",
    "NAVER_CLIENT_SECRET",
    "KAKAO_REST_API_KEY",
    "KAKAO_ACCESS_TOKEN",
    "KAKAO_REFRESH_TOKEN",
)


def _esc(val: str) -> str:
    val = val or ""
    if any(c in val for c in ' "\n\\\r#'):
        return '"' + val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r") + '"'
    return val


def main() -> None:
    lines: list[str] = []
    for k in REQUIRED:
        v = os.environ.get(k, "")
        if not str(v).strip():
            raise SystemExit(f"ci_write_env: missing required variable {k}")
        lines.append(f"{k}={_esc(v)}")
    for k in OPTIONAL:
        v = os.environ.get(k, "")
        if v is None or not str(v).strip():
            continue
        lines.append(f"{k}={_esc(v)}")
    Path(".env").write_text("\n".join(lines) + "\n", encoding="utf-8")
    keys_only = [ln.partition("=")[0] for ln in lines]
    print("Wrote .env for CI:", ", ".join(keys_only))


if __name__ == "__main__":
    main()
