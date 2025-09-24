# EML 분석 도구 모음

EML(이메일) 파일을 분석, 검색, 관리하는 Python 도구 모음입니다.

> 소스코드 저장소: [https://github.com/ygpark/eml_tool_py](https://github.com/ygpark/eml_tool_py)

---

## 설치 방법

Python 3.9 이상이 필요합니다. [uv](https://docs.astral.sh/uv/)를 사용하여 관리됩니다.

### uv 설치

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 프로젝트 설치

```bash
git clone https://github.com/ygpark/eml_tool_py.git
cd eml_tool_py

# 의존성 설치 및 가상환경 설정
uv sync

# 개발 도구 포함 설치
uv sync --dev
```

### CLI 도구 사용

uv가 가상환경을 자동 관리하므로 `uv run` 명령어로 도구를 실행할 수 있습니다:

```bash
# 직접 실행
uv run eml-list --help
uv run eml-search --help
uv run eml-rename --help

# 또는 Python 모듈로 실행
uv run python -m eml_tool_py.eml_list --help
```

---

## 도구 목록

### 1. eml-list.py - EML 파일 정보 추출

EML 파일들의 헤더 정보를 CSV 형식으로 출력합니다.

**사용법:**

```bash
uv run eml-list -i 입력경로 [-r]
```

**출력 컬럼:**

- File: 파일 경로
- Subject: 제목
- From: 발신자
- To: 수신자
- Date: 날짜 (yyyy-mm-dd hh:mm:ss +timezone)
- X-Originating-IP: 발신 IP 주소
- PHPMailer: PHPMailer 사용 여부 (Yes/No)

**예시:**

```bash
# 현재 디렉터리의 EML 파일 분석
uv run eml-list -i .

# 하위 디렉터리까지 재귀적으로 분석
uv run eml-list -i ./mail_folder -r
```

### 2. eml-rename.py - EML 파일명 일괄 변경

EML 파일을 날짜와 제목을 기반으로 한 표준 형식으로 이름을 변경합니다.

**파일명 형식:** `yyyy-mm-dd HHMMSS 제목_<8자리해시>.eml`

**사용법:**

```bash
uv run eml-rename [-r] [--mode {received,sent}] [--uniq {hash,none}] [--on-dup {suffix,skip,overwrite}] [--dry-run] PATH
```

**주요 옵션:**

- `-r`: 하위 디렉터리 재귀 탐색
- `--mode received`: 수신 날짜 기준 (기본값)
- `--mode sent`: 발신 날짜 기준
- `--uniq hash`: 8자리 해시 추가 (기본값)
- `--uniq none`: 해시 없이 날짜+제목만 사용
- `--dry-run`: 실제 변경 없이 미리보기만

**예시:**

```bash
# 현재 디렉터리의 EML 파일 이름 변경
uv run eml-rename .

# 하위 폴더까지 재귀적으로 처리
uv run eml-rename -r ./메일폴더

# 미리보기 (실제 변경 없음)
uv run eml-rename --dry-run ./inbox
```

### 3. eml-search.py - EML 파일 내용 검색

EML 파일의 헤더 또는 본문에서 정규식으로 내용을 검색하고, 매칭되는 파일을 필터링하거나 복사할 수 있습니다.

**사용법:**

```bash
uv run eml-search -i 입력디렉터리 -p '정규식패턴' [옵션]
```

**기본 검색 (헤더):**

```bash
uv run eml-search -i ./eml_folder -p 'PATTERN'
```

**본문 내용 검색:**

```bash
uv run eml-search -i ./eml_folder -p 'PATTERN' --body
```

**매칭된 파일 복사:**

```bash
uv run eml-search -i ./eml_folder -p 'PATTERN' -o ./matched_files
```

**매칭된 텍스트만 출력:**

```bash
uv run eml-search -i ./eml_folder -p 'https?://[^"\s]*(?:o-r\.kr|p-e\.kr)[^"\s]*' --body --match-only
```

**주요 옵션:**

- `-i`, `--input`: 입력 디렉터리 경로
- `-p`, `--pattern`: 검색할 정규 표현식 (필수)
- `--ignore-case`: 대소문자 구분 없이 검색
- `-o`, `--output`: 매칭된 파일을 복사할 디렉터리
- `-b`, `--body`: 헤더 대신 본문 검색 (첨부파일 제외)
- `--match-only`: 매칭된 텍스트만 출력

---

## 사용 예시

### 특정 도메인의 URL 찾기

```bash
uv run eml-search -i ./emails -p 'https?://[^"\s]*(?:example\.com|test\.org)[^"\s]*' --body --match-only
```

### 스팸 메일 식별

```bash
# PHPMailer를 사용한 메일 찾기
uv run eml-list -i ./emails -r | grep "Yes"

# 특정 IP에서 온 메일 찾기
uv run eml-list -i ./emails -r | grep "192.168.1.100"
```

### 메일 정리

```bash
# 1. 메일 파일명을 표준화
uv run eml-rename -r ./raw_emails

# 2. 특정 패턴의 메일을 별도 폴더로 분류
uv run eml-search -i ./raw_emails -p 'urgent|important' --ignore-case -o ./important_emails
```

---

## 개발자 도구

이 프로젝트는 [uv](https://docs.astral.sh/uv/)와 함께 Ruff, Black을 사용하여 코드 품질을 관리합니다.

### 사용 가능한 Make 명령어

```bash
# 도움말 보기
make help

# 개발 환경 설치
make dev

# 코드 포맷팅
make format

# 린팅 검사
make lint

# 린팅 + 자동 수정
make lint-fix

# 타입 체크
make type-check

# 모든 체크 수행
make check

# 패키지 빌드
make build

# 캐시 정리
make clean
```

### Pre-commit Hook

```bash
# pre-commit 설치 (선택사항)
uv add --dev pre-commit
uv run pre-commit install
```
