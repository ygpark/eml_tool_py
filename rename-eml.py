#!/usr/bin/env python3
# rename_eml.py
# -*- coding: utf‑8 -*-
"""
Rename .eml files using header date and subject:
    yyyy-mm-dd HHMMSS <subject>.eml
"""

from __future__ import annotations

import argparse
import email
import functools
import mailbox
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

# ----------------------------- CLI 정의 ----------------------------- #
_DESCRIPTION = """\
DESCRIPTION
    .eml 파일의 수신(기본) 또는 발신 날짜를 읽어
    'yyyy-mm-dd HHMMSS 제목.eml' 형식으로 파일명을 변경합니다.
"""

_EXAMPLES = """\
EXAMPLES
    # 현재 디렉터리의 .eml 파일만(재귀 X) 이름 변경
    python rename_eml.py .

    # 하위 폴더까지 재귀적으로 처리
    python rename_eml.py -r ./메일폴더

    # 변경 내용을 보여주기만 하고 실제로는 변경하지 않음
    python rename_eml.py --dry-run ~/Downloads

    # 발신일(From) 기준으로 이름을 변경
    python rename_eml.py --mode sent ./inbox
"""

_USAGE = "python rename_eml.py [-r] [--mode {received,sent}] [--dry-run] PATH [PATH ...]"

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rename_eml.py",
        usage=_USAGE,
        description=_DESCRIPTION,
        epilog=_EXAMPLES,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,  # 수동으로 -h / --help 추가
    )

    # ----- 기본 help 옵션(-h / --help) ----- #
    parser.add_argument(
        "-h", "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="이 도움말을 표시하고 종료합니다.",
    )

    # ----- 기타 옵션 ----- #
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="하위 디렉터리를 재귀적으로 탐색합니다.",
    )
    parser.add_argument(
        "--mode",
        choices=("received", "sent"),
        default="received",
        help="날짜 추출 기준을 선택합니다. 기본값: received",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="변경 사항을 출력만 하고 실제로 파일명을 수정하지 않습니다.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="진행 상황을 상세히 출력합니다.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="이름을 변경할 .eml 파일 또는 디렉터리 경로(여러 개 지정 가능).",
    )
    return parser
# -------------------------------------------------------------------- #

_SUBJECT_RE = re.compile(r'[\\/:*?"<>|\r\n]+')

def _safe_subject(subject: str) -> str:
    """파일명에 쓸 수 없는 문자를 제거"""
    clean = _SUBJECT_RE.sub(" ", subject).strip()
    return clean or "untitled"

def _extract_datetime(msg: email.message.Message, mode: str) -> datetime | None:
    header = "Date" if mode == "received" else "Sent"
    hdr_val = msg.get(header) or msg.get("Date")
    try:
        return email.utils.parsedate_to_datetime(hdr_val)
    except Exception:
        return None

def _rename_file(file_path: Path, mode: str, dry_run: bool, verbose: bool) -> None:
    try:
        with file_path.open("rb") as f:
            msg = email.message_from_binary_file(f)
    except Exception as e:
        print(f"[ERR] {file_path!s}: {e}", file=sys.stderr)
        return

    dt = _extract_datetime(msg, mode)
    subject = _safe_subject(msg.get("Subject", ""))
    if not dt:
        print(f"[SKIP] 날짜를 찾을 수 없음: {file_path!s}")
        return

    new_name = f"{dt.strftime('%Y-%m-%d %H%M%S')} {subject}.eml"
    new_path = file_path.with_name(new_name)

    if verbose or dry_run:
        print(f"{'[DRY‑RUN] ' if dry_run else ''}{file_path.name}  →  {new_path.name}")

    if not dry_run:
        try:
            file_path.rename(new_path)
        except Exception as e:
            print(f"[ERR] 이름 변경 실패: {file_path!s}: {e}", file=sys.stderr)

def _iter_target_files(paths: Iterable[str], recursive: bool) -> List[Path]:
    files: List[Path] = []
    for p in map(Path, paths):
        if p.is_file() and p.suffix.lower() == ".eml":
            files.append(p)
        elif p.is_dir():
            pattern = "**/*.eml" if recursive else "*.eml"
            files.extend(p.glob(pattern))
    return files

def main(argv: List[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    files = _iter_target_files(args.paths, args.recursive)
    if not files:
        print("처리할 .eml 파일이 없습니다.", file=sys.stderr)
        sys.exit(1)

    for f in files:
        _rename_file(f, args.mode, args.dry_run, args.verbose)

if __name__ == "__main__":
    main()
