# helper-plot-hangul uv 업로드 가이드

## 1. 개발 환경 동기화
```bash
uv sync
```

## 2. 패키지 빌드
```bash
uv run python -m build
```

## 3. TestPyPI에 업로드 (테스트용)
```bash
uv run python -m twine upload --repository testpypi dist/*
```

## 4. PyPI에 업로드 (배포용)
```bash
uv run python -m twine upload dist/*
```

## 5. 설치 테스트
```bash
# TestPyPI에서 설치
pip install --index-url https://test.pypi.org/simple/ helper-plot-hangul

# PyPI에서 설치
pip install helper-plot-hangul
```

## 주의사항
- `build`, `twine`, `pip`는 배포용 개발 의존성으로 관리됩니다.
- Streamlit 감지가 필요하면 `uv sync --extra streamlit` 또는 `pip install "helper-plot-hangul[streamlit]"`를 사용합니다.
- PyPI 계정이 필요합니다 (https://pypi.org/account/register/)
- 버전 번호는 한번 업로드하면 같은 번호로 재업로드 불가
- 업로드 전 반드시 로컬에서 테스트 후 진행
