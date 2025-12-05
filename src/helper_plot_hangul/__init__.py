"""
helper-plot-hangul
==================

Matplotlib 한글 폰트 자동 설정 라이브러리

주요 기능:
- 자동 폰트 설정: NanumGothic 폰트를 자동으로 로드하고 설정
- 완전한 matplotlib 리셋: 폰트 캐시를 포함한 완전한 초기화
- 스타일 호환: matplotlib 스타일 적용 후에도 한글 폰트 자동 유지
- Jupyter/Colab 최적화: IPython 환경에서 완벽하게 작동

기본 사용법:
    from helper_plot_hangul import matplotlib_font_reset
    
    plt = matplotlib_font_reset()
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title('한글 제목')
    plt.show()
"""

__version__ = "0.5.0"

from .helper_plot_hangul import matplotlib_font_reset, matplotlib_font_set

__all__ = [
    "matplotlib_font_reset",
    "matplotlib_font_set",
    "__version__",
]
