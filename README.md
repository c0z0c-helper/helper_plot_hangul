# helper-plot-hangul

Matplotlib 한글 폰트 자동 설정 라이브러리

## 개요

`helper-plot-hangul`은 Matplotlib에서 한글을 자동으로 표시할 수 있도록 폰트를 설정해주는 라이브러리입니다. 번거로운 폰트 설정 없이 간단하게 한글 그래프를 그릴 수 있습니다.

## 특징

- **자동 폰트 설정**: NanumGothic 폰트를 자동으로 로드하고 설정
- **완전한 matplotlib 리셋**: 폰트 캐시를 포함한 완전한 초기화
- **스타일 호환**: matplotlib 스타일 적용 후에도 한글 폰트 자동 유지
- **Jupyter/Colab 최적화**: IPython 환경에서 완벽하게 작동
- **NumPy 2.0+ 호환**: 최신 NumPy와 호환되는 안전한 폰트 설정
- **내장 폰트**: NanumGothic 폰트 포함 (별도 설치 불필요)

## 설치

```bash
pip install helper-plot-hangul

# 테스트 서버
pip install --index-url https://test.pypi.org/simple/ helper-plot-hangul
```

## 사용법

### 기본 사용법

```python
from helper_plot_hangul import matplotlib_font_reset

# 한글 폰트 자동 설정 (NanumGothic 기본값)
plt = matplotlib_font_reset()

# 바로 한글 사용 가능
plt.plot([1, 2, 3], [1, 4, 9])
plt.title('한글 제목')
plt.xlabel('X축')
plt.ylabel('Y축')
plt.show()
```

### 사용자 정의 폰트 사용

```python
from helper_plot_hangul import matplotlib_font_reset

# 시스템 폰트 이름으로 설정
plt = matplotlib_font_reset(font_family='맑은 고딕')

# 또는 폰트 파일 경로로 설정
plt = matplotlib_font_reset(font_path='/path/to/font.ttf')
```

### 추가 옵션 설정

```python
from helper_plot_hangul import matplotlib_font_reset

# matplotlib rcParams 추가 설정
plt = matplotlib_font_reset(
    font_family='NanumGothic',
    axes_unicode_minus=False,  # 마이너스 기호 깨짐 방지
    font_size=12,              # 기본 폰트 크기
)
```

### 스타일과 함께 사용

```python
from helper_plot_hangul import matplotlib_font_reset

# 한글 폰트 먼저 설정
plt = matplotlib_font_reset()

# 스타일 적용 (한글 폰트 자동 유지)
plt.style.use('seaborn-v0_8-whitegrid')

plt.plot([1, 2, 3], [1, 4, 9])
plt.title('스타일 적용 + 한글')
plt.show()
```

### Jupyter/Colab에서 사용

```python
from helper_plot_hangul import matplotlib_font_reset

# 최초 1회만 실행
matplotlib_font_reset()

# 이후 셀에서 plt 바로 사용 가능
import matplotlib.pyplot as plt

plt.plot([1, 2, 3], [1, 4, 9])
plt.title('주피터에서 한글')
plt.show()
```

### 선호 폰트만 등록 (리셋 없이)

```python
from helper_plot_hangul import matplotlib_font_set

# matplotlib 리셋 없이 폰트만 변경
matplotlib_font_set(font_family='맑은 고딕', font_size=11)
```

## API 레퍼런스

### `matplotlib_font_reset(font_family=None, font_path=None, **kwargs)`

matplotlib를 완전히 리셋하고 한글 폰트를 설정합니다.

**Parameters:**
- `font_family` (str, optional): 사용할 폰트 패밀리 이름 (기본값: 'NanumGothic')
- `font_path` (str, optional): 폰트 파일 경로. 지정 시 파일에서 폰트 이름 추출
- `**kwargs`: matplotlib rcParams에 전달할 추가 설정
  - `axes_unicode_minus` (bool): 마이너스 기호 깨짐 방지 (기본값: False)
  - `font_size` (int): 기본 폰트 크기 (기본값: 10)

**Returns:**
- `matplotlib.pyplot`: 리셋되고 한글 폰트가 설정된 pyplot 모듈

**폰트 설정 우선순위:**
1. `font_path`가 있으면 파일에서 폰트 패밀리 이름 추출
2. `font_family`만 있으면 해당 이름 사용
3. 둘 다 없으면 'NanumGothic' 기본값 사용 + 자동 탐색

### `matplotlib_font_set(font_family=None, font_path=None, **kwargs)`

matplotlib를 리셋하지 않고 선호 폰트만 등록하고 즉시 적용합니다.

**Parameters:**
- `font_family` (str, optional): 사용할 폰트 패밀리 이름
- `font_path` (str, optional): 폰트 파일 경로
- `**kwargs`: matplotlib rcParams에 전달할 추가 설정

## 작동 원리

1. **폰트 자동 탐색**: 패키지에 내장된 NanumGothic 폰트를 자동으로 찾아 로드
2. **완전한 리셋**: matplotlib 모듈을 완전히 리로드하여 폰트 캐시 클리어
3. **스타일 패치**: `matplotlib.style.use` 함수를 패치하여 스타일 적용 후 자동으로 한글 폰트 재설정
4. **전역 등록**: IPython 환경과 호출자 네임스페이스에 plt를 자동 등록

## 문제 해결

### 한글이 여전히 깨져 보이는 경우

```python
# 1. 완전 리셋 시도
from helper_plot_hangul import matplotlib_font_reset
plt = matplotlib_font_reset()

# 2. 폰트 캐시 수동 삭제 (필요시)
import matplotlib.font_manager as fm
fm._get_fontconfig_fonts.cache_clear()
```

### 특정 폰트 사용하고 싶은 경우

```python
# 시스템에 설치된 폰트 사용
plt = matplotlib_font_reset(font_family='D2Coding')

# 폰트 파일 직접 지정
plt = matplotlib_font_reset(font_path='/usr/share/fonts/custom.ttf')
```

## 요구사항

- Python >= 3.8
- matplotlib >= 3.2.0

## 라이센스

MIT License

## 기여

버그 리포트나 기능 제안은 [GitHub Issues](https://github.com/c0z0c-helper/helper_plot_hangul/issues)에 등록해주세요.

## 변경 이력

### v0.5.0(2025-12-05)
- 최초 릴리스
- NanumGothic 폰트 내장
- matplotlib 완전 리셋 기능
- 스타일 호환성 자동 패치
- Jupyter/Colab 최적화

### v0.5.1(2025-12-09)
- github 주소 변경

### v0.5.2(2025-12-10)
- jyupyter, colab 에서만 plot reset
- 다른 환경에서는 폰트만 로딩

### v0.5.3(2025-12-11)
- 종속 라이브러리 설치

---

jupyter_hangul를 참고하여 만들어졌습니다.
- https://c0z0c.github.io/jupyter_hangul/

