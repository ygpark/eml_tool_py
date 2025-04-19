# 파일명: emlheadpick.py

import argparse
import os
import re

def has_keyword_in_header(filepath, pattern):
    try:
        with open(filepath, 'rb') as f:
            header_lines = []
            for line in f:
                if line in (b'\n', b'\r\n'):
                    break
                header_lines.append(line)
            header_content = b''.join(header_lines).decode(errors='ignore')
            return bool(pattern.search(header_content))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="EML 파일 헤더를 검색하여 정규식에 매칭되는 파일 경로를 출력합니다.")
    parser.add_argument('--input', '-i', required=True, help='입력 디렉토리 경로')
    parser.add_argument('--pattern', '-p', required=True, help='헤더에서 찾을 정규 표현식')
    args = parser.parse_args()

    input_dir = args.input
    regex_pattern = args.pattern
    try:
        pattern = re.compile(regex_pattern, flags=re.IGNORECASE)
    except re.error as e:
        print(f"Invalid regular expression: {e}")
        return

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.eml'):
                filepath = os.path.join(root, file)
                if has_keyword_in_header(filepath, pattern):
                    print(filepath)

if __name__ == '__main__':
    main()

