# grep-emlheader

EML 파일의 헤더를 검색하여 정규 표현식에 매칭되는 파일을 찾거나 복사하는 Python CLI 도구입니다.

---

## ✨ 특징

- EML 파일의 **헤더 부분만** 읽고 검색합니다.
- **정규 표현식(Regex)** 으로 원하는 패턴을 검색할 수 있습니다.
- 대소문자 구분 **옵션** 제공 (`--ignore-case`).
- 검색된 파일을 **출력하거나 복사**할 수 있습니다.
- 빠르고, 대용량 파일에도 메모리 효율적입니다.

---

## 📦 설치

Python 3.7 이상이 필요합니다.

```bash
git clone https://github.com/yourname/grep-emlheader.git
cd grep-emlheader
