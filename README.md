# grep-eml.py

EML의 헤더 또는 본문 내용을 정규식(정규 표현식)으로 검색하고, 매칭되는 파일만 필터링하거나, 원본 파일을 복사할 수 있는 CLI 프로그램입니다.

> 소스코드 저장소: [https://github.com/ygpark/eml_tool_py](https://github.com/ygpark/eml_tool_py)

---

## 설치 방법

최적화된 파이썬 3.x 프로그램이 필요합니다.

GitHub 저장소를 클론합니다:

```bash
git clone https://github.com/ygpark/eml_tool_py.git
cd eml_tool_py
```

---

## 사용 방법

### 기본 검색 (헤더)

헤더에서 `PATTERN` 패턴을 검색합니다.

```bash
./grep-eml.py -i ./eml_folder -p 'PATTERN'
```

헤더에서 `PATTERN` 패턴을 검색하고, 검색된 파일을 지정한 폴더로 복사합니다.

```bash
./grep-eml.py -i ./eml_folder -p 'PATTERN' -o ./matched_files
```

### 본문(Body) 내용을 검색

헤더가 아니라 본문 내용을 검색하려면 `--body` 옵션을 추가합니다.

```bash
./grep-eml.py -i ./eml_folder -p 'PATTERN' --body
```

### 매칭된 텍스트만 출력

파일 경로 대신 해당 파일 내에서 매칭된 텍스트만 출력하고 싶을 경우:

```bash
./grep-eml.py -i ./eml_folder -p 'https?://[^"\s]*(?:o-r\.kr|p-e\.kr)[^"\s]*' --body --match-only
```

출력 예시:

```
https://example.p-e.kr/login
http://o-r.kr/path?param=wreply
...
```

---

## 옵션 정보

| 옵션 | 개요 |
|:---|:---|
| `-i`, `--input` | 파일이 들어있는 입력 디렉터리 |
| `-p`, `--pattern` | 검색할 정규 표현식 (필수) |
| `--ignore-case` | 대소문자 구분 없이 검색 |
| `-o`, `--output` | 매칭된 파일을 복사할 디렉터리 |
| `-b`, `--body` | 헤더 대신 본문 검색 |
| `--match-only` | 매칭된 텍스트나 URL만 출력, 파일명 출력 없음 |

