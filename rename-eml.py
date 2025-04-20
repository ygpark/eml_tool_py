#!/usr/bin/env python3
"""
.eml 파일을 'YYYY-MM-DD HHMMSS 제목.eml' 형식으로 변경합니다.

옵션
  -i, --input <경로>        단일 .eml 파일 또는 디렉터리
  -r, --recursive           하위 폴더까지 재귀적으로 처리
  --prefer-received         Date 대신 가장 오래된 Received 헤더 사용
  -n, --dry-run             실제 변경 없이 미리보기
  -f, --force               동일 이름 존재 시 덮어쓰기

작성: 2025‑04‑20
Python 3.9 이상 필요(zoneinfo 사용)
"""

from __future__ import annotations

import argparse
import email
import email.policy
import email.utils
import html
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# ────────────── 설정값 ──────────────
LOCAL_TZ = ZoneInfo("Asia/Seoul")          # 필요 시 타임존 변경
INVALID_CHARS = re.compile(r'[\\/*?:"<>|]+')
MAX_NAME_LEN = 100                         # 제목 최대 길이
# ────────────────────────────────────


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rename .eml files by header metadata")
    p.add_argument("-i", "--input", required=True,
                   help="단일 .eml 파일 또는 디렉터리 경로")
    p.add_argument("-r", "--recursive", action="store_true",
                   help="하위 폴더까지 재귀적으로 처리")
    p.add_argument("-n", "--dry-run", action="store_true",
                   help="실행하지 않고 변경될 이름만 출력")
    p.add_argument("-f", "--force", action="store_true",
                   help="동일 이름 존재 시 덮어쓰기")
    p.add_argument("--prefer-received", action="store_true",
                   help="Date 대신 가장 오래된 Received 헤더 사용")
    return p.parse_args()


def extract_date(msg: email.message.Message,
                 prefer_received: bool = False) -> datetime | None:
    """헤더에서 날짜를 datetime(LOCAL_TZ) 로 반환"""
    date_str = None

    if prefer_received:
        recv = msg.get_all("Received", [])
        if recv:
            # 마지막(=가장 오래된) Received 헤더의 세미콜론 뒤 날짜
            m = re.search(r";\s*(.+)$", recv[-1])
            if m:
                date_str = m.group(1).strip()

    if date_str is None:
        date_str = msg.get("Date")

    if date_str is None:
        return None

    try:
        dt = email.utils.parsedate_to_datetime(date_str)
    except (TypeError, ValueError):
        return None

    # tz 정보가 없으면 LOCAL_TZ 부여, 있으면 LOCAL_TZ 로 변환
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=LOCAL_TZ)
    return dt.astimezone(LOCAL_TZ)


def safe_subject(raw_subj: str | None) -> str:
    """제목에서 금지 문자 제거·길이 제한"""
    if not raw_subj:
        return "No Subject"
    subj = html.unescape(raw_subj).strip()
    subj = INVALID_CHARS.sub("", subj)         # \ / : * ? " < > |
    subj = re.sub(r"\s+", " ", subj)           # 연속 공백 정리
    return subj[:MAX_NAME_LEN] or "No Subject"


def new_filename(dt: datetime | None, subject: str) -> str:
    """'YYYY-MM-DD HHMMSS 제목.eml' 파일명 생성"""
    stamp = dt.strftime("%Y-%m-%d %H%M%S") if dt else "1970-01-01 000000"
    return f"{stamp} {subject}.eml"


def rename_file(path: Path, args: argparse.Namespace) -> None:
    """단일 .eml 파일 이름 변경"""
    try:
        msg = email.message_from_binary_file(path.open("rb"),
                                             policy=email.policy.default)
    except Exception as e:
        print(f"[ERROR] '{path}': {e}", file=sys.stderr)
        return

    dt = extract_date(msg, args.prefer_received)
    subject = safe_subject(msg.get("Subject"))
    new_name = new_filename(dt, subject)
    target = path.with_name(new_name)

    # 이름 충돌 처리
    if target.exists() and not args.force:
        idx = 1
        while (alt := target.with_stem(f"{target.stem}_{idx}")).exists():
            idx += 1
        target = alt

    if args.dry_run:
        print(f"[DRY] '{path.name}' → '{target.name}'")
        return

    try:
        path.rename(target)
        print(f"[OK ] '{path.name}' → '{target.name}'")
    except FileExistsError:
        print(f"[SKIP] '{target.name}' 이미 존재 (--force 필요)", file=sys.stderr)
    except Exception as e:
        print(f"[FAIL] '{path.name}': {e}", file=sys.stderr)


def main() -> None:
    args = parse_args()
    root = Path(args.input).expanduser().resolve()

    # 입력 경로 유효성
    if not root.exists():
        sys.exit(f"[FAIL] 경로가 존재하지 않습니다: '{root}'")

    # 파일/디렉터리 분기
    if root.is_file():
        if root.suffix.lower() != ".eml":
            sys.exit("[FAIL] *.eml 파일을 지정하세요.")
        paths = [root]
    else:
        pattern = "**/*.eml" if args.recursive else "*.eml"
        paths = list(root.glob(pattern))

    if not paths:
        sys.exit("[INFO] 대상 .eml 파일이 없습니다.")

    for p in paths:
        rename_file(p, args)


if __name__ == "__main__":
    main()
