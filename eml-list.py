#!/usr/bin/env python3
"""
EML 분석 도구 (CSV 출력 + X-Originating-IP + PHPMailer 검사 + 날짜 포맷)

Usage:
    python eml_list.py -i 입력경로 [-r]
"""
import argparse
import os
import sys
import csv
import io
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

def process_file(filepath):
    with open(filepath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    subject = msg['subject'] or ''
    from_ = msg['from'] or ''
    to = msg['to'] or ''
    # 날짜 파싱 및 포맷: yyyy-mm-dd hh:mm:ss +0900
    date_hdr = msg['date'] or ''
    try:
        dt = parsedate_to_datetime(date_hdr)
        # datetime이 timezone-aware인지 확인, 없으면 그대로 출력
        date = dt.strftime('%Y-%m-%d %H:%M:%S %z')
    except Exception:
        date = date_hdr
    x_ip = msg.get('X-Originating-IP', '').strip('[]')
    # PHPMailer 문자열 포함 여부 확인
    phpmailer_flag = 'Yes' if any('PHPMailer' in str(v) for v in msg.values()) else 'No'
    return [filepath, subject, from_, to, date, x_ip, phpmailer_flag]

def gather_paths(input_path, recursive):
    paths = []
    if os.path.isdir(input_path):
        if recursive:
            for root, _, files in os.walk(input_path):
                for name in files:
                    if name.lower().endswith('.eml'):
                        paths.append(os.path.join(root, name))
        else:
            for name in os.listdir(input_path):
                if name.lower().endswith('.eml'):
                    paths.append(os.path.join(input_path, name))
    elif os.path.isfile(input_path) and input_path.lower().endswith('.eml'):
        paths.append(input_path)
    else:
        sys.exit('유효한 EML 파일 또는 디렉토리가 아닙니다.')
    return paths

def main():
    # Windows 콘솔 출력에서 utf-8 인코딩 보장
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')

    parser = argparse.ArgumentParser(
        description='EML 분석 도구 (CSV 출력 + X-Originating-IP + PHPMailer 검사 + 날짜 포맷)'
    )
    parser.add_argument('-i', '--input', required=True, help='EML 파일 또는 디렉토리 경로')
    parser.add_argument('-r', '--recursive', action='store_true', help='디렉토리 재귀 탐색')
    args = parser.parse_args()

    paths = gather_paths(args.input, args.recursive)

    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(['File', 'Subject', 'From', 'To', 'Date', 'X-Originating-IP', 'PHPMailer'])
    for p in paths:
        row = process_file(p)
        writer.writerow(row)

if __name__ == '__main__':
    main()
