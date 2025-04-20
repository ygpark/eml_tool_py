#!/usr/bin/env python3
# rename_eml.py
# -*- coding: utf-8 -*-
"""
Rename .eml files to the format:

    yyyy-mm-dd HHMMSS <subject>_<8‑char hash>.eml
"""

from __future__ import annotations

import argparse
import email
import hashlib
import os
import re
import sys
from datetime import datetime
from email.header import decode_header, make_header
from pathlib import Path
from typing import Iterable, List

# ──────────────────────── 도움말 텍스트 ──────────────────────── #
_DESCRIPTION = """\
DESCRIPTION
    .eml 파일의 수신(기본) 또는 발신 날짜를 읽어
    'yyyy-mm-dd HHMMSS 제목_<해시>.eml' 형식으로 파일명을 변경합니다.
    해시는 SHA‑256 값의 앞 8자이며, 동일 날짜·제목이라도 파일이 다르면
    충돌 없이 고유한 이름이 보장됩니다.
"""

_EXAMPLES = """\
EXAMPLES
    # 현재 디렉터리의 .eml 파일만(재귀 X) 이름 변경
    python rename_eml.py .

    # 하위 폴더까지 재귀적으로 처리
    python rename_eml.py -r ./메일폴더

    # 해시 없이 날짜+제목만 사용
    python rename_eml.py --uniq none ./inbox
"""

_USAGE = ("python rename_eml.py [-r] [--mode {received,sent}] "
          "[--uniq {hash,none}] [--on-dup {suffix,skip,overwrite}] "
          "[--dry-run] PATH [PATH ...]")

# ──────────────────────── 파서 빌더 ──────────────────────── #
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rename_eml.py",
        usage=_USAGE,
        description=_DESCRIPTION,
        epilog=_EXAMPLES,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )

    parser.add_argument("-h", "--help",
                        action="help",
                        default=argparse.SUPPRESS,
                        help="이 도움말을 표시하고 종료합니다.")

    parser.add_argument("-r", "--recursive", action="store_true",
                        help="하위 디렉터리를 재귀적으로 탐색합니다.")
    parser.add_argument("--mode", choices=("received", "sent"),
                        default="received",
                        help="날짜 추출 기준(기본: received).")
    parser.add_argument("--uniq", choices=("hash", "none"),
                        default="hash",
                        help="짧은 해시(hash) 또는 사용 안 함(none), 기본: hash.")
    parser.add_argument("--on-dup",
                        choices=("suffix", "skip", "overwrite"),
                        default="suffix",
                        help=("동일 이름이 이미 존재할 때 동작 "
                              "(suffix|skip|overwrite, 기본: suffix)."))
    parser.add_argument("--dry-run", action="store_true",
                        help="변경 사항을 출력만 하고 실제로 수정하지 않습니다.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="진행 상황을 상세히 출력합니다.")
    parser.add_argument("paths", nargs="+",
                        help=".eml 파일 또는 디렉터리 경로(여러 개 가능).")
    return parser

# ──────────────────────── 유틸리티 ──────────────────────── #
_SUBJECT_RE = re.compile(r'[\\/:*?"<>|\r\n]+')

def _safe_subject(subject: str, max_len: int = 120) -> str:
    cleaned = _SUBJECT_RE.sub(" ", subject).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return (cleaned[:max_len].rstrip() if len(cleaned) > max_len else cleaned) or "untitled"

def _get_subject(msg: email.message.Message) -> str:
    raw = msg.get("Subject", "")
    try:
        return str(make_header(decode_header(raw)))
    except Exception:
        return raw

def _extract_datetime(msg: email.message.Message, mode: str) -> datetime | None:
    hdr_val = msg.get("Date")
    try:
        return email.utils.parsedate_to_datetime(hdr_val)
    except Exception:
        return None

def _short_hash(path: Path, length: int = 8) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:length]

def _unique_path(base: Path) -> Path:
    if not base.exists():
        return base
    stem, suffix = base.stem, base.suffix
    for i in range(1, 10000):
        candidate = base.with_name(f"{stem} ({i}){suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"너무 많은 중복: {base!s}")

# ──────────────────────── 핵심 로직 ──────────────────────── #
def _rename_file(file_path: Path,
                 mode: str,
                 uniq: str,
                 on_dup: str,
                 dry_run: bool,
                 verbose: bool) -> None:
    try:
        with file_path.open("rb") as f:
            msg = email.message_from_binary_file(f)
    except Exception as e:
        print(f"[ERR] {file_path!s}: {e}", file=sys.stderr)
        return

    dt = _extract_datetime(msg, mode)
    subject = _safe_subject(_get_subject(msg))
    if not dt:
        print(f"[SKIP] 날짜를 찾을 수 없음: {file_path!s}")
        return

    base_name = f"{dt.strftime('%Y-%m-%d %H%M%S')} {subject}"
    if uniq == "hash":
        base_name += f"_{_short_hash(file_path)}"

    target = file_path.with_name(base_name + ".eml")

    # 중복 처리
    if target.exists():
        if on_dup == "skip":
            print(f"[SKIP] 이미 존재: {target.name}")
            return
        if on_dup == "overwrite":
            pass
        else:  # suffix
            target = _unique_path(target)

    if verbose or dry_run:
        action = "→" if not dry_run else "(DRY‑RUN) →"
        print(f"{file_path.name} {action} {target.name}")

    if not dry_run:
        try:
            os.replace(file_path, target)
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

# ──────────────────────── 메인 ──────────────────────── #
def main(argv: List[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    files = _iter_target_files(args.paths, args.recursive)
    if not files:
        print("처리할 .eml 파일이 없습니다.", file=sys.stderr)
        sys.exit(1)

    for f in files:
        _rename_file(f, args.mode, args.uniq, args.on_dup,
                     args.dry_run, args.verbose)

if __name__ == "__main__":
    main()
