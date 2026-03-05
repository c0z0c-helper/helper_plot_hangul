"""python -m helper_plot_hangul 실행 진입점 (표준 사용법 동작 확인용)."""

import matplotlib.pyplot as plt
from helper_plot_hangul import matplotlib_font_reset

# --- 표준 사용법 1: import 후 style.use + 한글 타이틀 ---
plt.style.use("seaborn-v0_8-whitegrid")
plt.plot([1, 2, 3], [1, 4, 9])
plt.title("자동 초기화: NanumGothic")
plt.xlabel("X축")
plt.ylabel("Y축")
plt.tight_layout()
plt.show()

# --- 표준 사용법 2: plt.rc로 다른 폰트 전환 ---
plt.rc("font", family="NanumBarunGothic")
plt.figure()
plt.plot([1, 2, 3], [9, 4, 1])
plt.title("plt.rc 전환: NanumBarunGothic")
plt.xlabel("X축")
plt.ylabel("Y축")
plt.tight_layout()
plt.show()

# --- 사용법 3: matplotlib_font_reset()으로 명시적 리셋 ---
plt = matplotlib_font_reset()
plt.style.use("ggplot")
plt.plot([1, 2, 3], [3, 1, 2])
plt.title("reset 후 ggplot 스타일: NanumGothic 유지")
plt.xlabel("X축")
plt.ylabel("Y축")
plt.tight_layout()
plt.show()
