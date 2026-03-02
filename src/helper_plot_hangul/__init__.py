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
    import matplotlib.pyplot as plt
    from helper_plot_hangul import matplotlib_font_reset

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title("한글 폰트 테스트")
    plt.xlabel("X축")
    plt.ylabel("Y축")
    plt.show()
"""

__version__ = "0.5.7"

import os
import sys
from pathlib import Path
import importlib.util

_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

spec = importlib.util.spec_from_file_location(
    "requirements_rnac", os.path.join(os.path.dirname(__file__), "requirements_rnac.py")
)
requirements_rnac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(requirements_rnac)
requirements_rnac.check_and_print_dependencies()

from helper_plot_hangul.helper_plot_hangul import (
    matplotlib_font_reset,
    matplotlib_font_set,
    matplotlib_font_get,
)

__all__ = [
    "matplotlib_font_reset",
    "matplotlib_font_set",
    "matplotlib_font_get",
    "__version__",
]
