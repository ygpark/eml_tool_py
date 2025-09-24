.PHONY: help install dev format lint type-check check test clean

help: ## 사용 가능한 명령어 목록 표시
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 프로젝트 설치
	uv sync

dev: ## 개발 환경 설치
	uv sync --dev

format: ## 코드 포맷팅 (black + ruff)
	uv run black src/ --check --diff
	uv run ruff format src/ --diff
	uv run black src/
	uv run ruff format src/

lint: ## 코드 린팅 (ruff)
	uv run ruff check src/

lint-fix: ## 코드 린팅 + 자동 수정 (ruff)
	uv run ruff check src/ --fix

type-check: ## 타입 체크 (mypy)
	uv run mypy src/

check: lint type-check ## 모든 체크 수행

test: ## 테스트 실행
	@echo "테스트 프레임워크가 설정되지 않았습니다."

clean: ## 캐시 및 빌드 파일 정리
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

build: ## 패키지 빌드
	uv build

run-list: ## eml-list 명령어 실행 (예시)
	uv run eml-list --help

run-rename: ## eml-rename 명령어 실행 (예시)  
	uv run eml-rename --help

run-search: ## eml-search 명령어 실행 (예시)
	uv run eml-search --help