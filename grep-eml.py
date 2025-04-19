#!/home/ghostyak/.local/bin/python
import argparse
import os
import re
import shutil
from email import policy
from email.parser import BytesParser

def extract_text_from_body(filepath):
    try:
        with open(filepath, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
        body_parts = []

        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = part.get_content_disposition()

            if content_disposition in ('attachment', 'inline'):
                continue  # 첨부파일은 제외

            if content_type in ('text/plain', 'text/html'):
                try:
                    body = part.get_content()
                    if body:
                        body_parts.append(str(body))
                except Exception as e:
                    print(f"본문 파싱 오류 ({filepath}): {e}")

        return "\n".join(body_parts)

    except Exception as e:
        print(f"이메일 파싱 실패: {filepath}: {e}")
        return ""

def extract_text_from_header(filepath):
    try:
        with open(filepath, 'rb') as f:
            header_lines = []
            for line in f:
                if line in (b'\n', b'\r\n'):
                    break
                header_lines.append(line)
            header_content = b''.join(header_lines).decode(errors='ignore')
            return header_content
    except Exception as e:
        print(f"헤더 읽기 실패: {filepath}: {e}")
        return ""

def has_keyword(filepath, pattern, search_body=False):
    if search_body:
        content = extract_text_from_body(filepath)
    else:
        content = extract_text_from_header(filepath)

    return bool(pattern.search(content))

def main():
    parser = argparse.ArgumentParser(description="EML 파일 헤더 또는 본문을 검색하여 정규식에 매칭되는 파일 경로를 출력하거나 복사합니다.")
    parser.add_argument('-i', '--input', required=True, help='입력 디렉토리 경로')
    parser.add_argument('-p', '--pattern', required=True, help='찾을 정규 표현식')
    parser.add_argument('--ignore-case', action='store_true', help='대소문자 구분 없이 검색')
    parser.add_argument('-o', '--output', help='매칭된 파일을 복사할 출력 디렉토리')
    parser.add_argument('-b', '--body', action='store_true', help='헤더 대신 본문을 검색합니다 (첨부파일 제외)')
    args = parser.parse_args()

    input_dir = args.input
    regex_pattern = args.pattern
    ignore_case = args.ignore_case
    output_dir = args.output
    search_body = args.body

    flags = re.IGNORECASE if ignore_case else 0

    try:
        pattern = re.compile(regex_pattern, flags=flags)
    except re.error as e:
        print(f"Invalid regular expression: {e}")
        return

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 순차적으로 파일 처리
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.eml'):
                filepath = os.path.join(root, file)
                try:
                    if has_keyword(filepath, pattern, search_body):
                        if output_dir:
                            dest_path = os.path.join(output_dir, os.path.basename(filepath))
                            shutil.copy2(filepath, dest_path)
                            print(f"복사 완료: {filepath} -> {dest_path}")
                        else:
                            print(filepath)
                except Exception as e:
                    print(f"처리 실패: {filepath}: {e}")

if __name__ == '__main__':
    main()
