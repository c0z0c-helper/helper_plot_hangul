"""공개 API: matplotlib 한글 폰트 설정 함수."""

import os
import sys
from pathlib import Path
from typing import Any

from helper_plot_hangul._env import is_jupyter_environment, is_streamlit_environment
from helper_plot_hangul._font_resource import matplotlib_font_resource
from helper_plot_hangul._font_utils import (
    get_preferred,
    patch_rcparams_default,
    patch_rcparams_setitem,
    reapply_font_rcparams,
    set_preferred,
)
from helper_plot_hangul._logger import logger

try:
    import IPython

    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False


def matplotlib_font_reset(
    font_family: str | None = None, font_path: str | None = None, **kwargs: Any
) -> Any:
    """커널 재시작 없이 한글 폰트를 즉시 적용.

    sys.modules 삭제 없이 font_manager의 내부 캐시를 무효화하고
    rcParams를 설정합니다. 기존 matplotlib/seaborn 객체의 클래스 동일성을
    유지하므로 Jupyter inline backend와 충돌하지 않습니다.

    matplotlib는 findfont() 결과를 내부 LRU 캐시에 저장합니다.
    단순 addfont() + rcParams 변경만으로는 캐시된 결과가 유지되어 새 폰트가
    반영되지 않습니다. 이 함수는 해당 캐시를 명시적으로 무효화합니다.

    Parameters
    ----------
    font_family : str, optional
        사용할 폰트 패밀리 이름 (기본값: 'NanumGothic')
    font_path : str, optional
        폰트 파일 경로. 지정 시 파일에서 폰트 이름 추출 (우선순위 최상위)
    **kwargs
        matplotlib rcParams에 전달할 추가 설정 (기본값: axes.unicode_minus=False, font.size=10)

    Returns
    -------
    matplotlib.pyplot
        한글 폰트가 설정된 pyplot 모듈.

    Notes
    -----
    폰트 설정 우선순위:
    1. font_path가 있으면 파일에서 폰트 패밀리 이름 추출
    2. font_family만 있으면 해당 이름 사용
    3. 둘 다 없으면 'NanumGothic' 기본값 사용
    """
    import matplotlib
    import matplotlib.font_manager as fm
    import matplotlib.pyplot as plt

    if (
        isinstance(font_family, (str, bytes, os.PathLike))
        and font_family
        and os.path.exists(font_family)
    ):
        font_path = str(font_family)
        font_family = None

    default_kwargs: dict = {"axes.unicode_minus": False, "font.size": 10}
    default_kwargs.update(kwargs)

    # 1. 패키지 번들 폰트 등록
    matplotlib_font_resource.load_all()

    # 2. font_path/font_family 결정
    if font_path is None and font_family is None:
        font_family = "NanumGothic"
        font_path = matplotlib_font_resource.path_of("NanumGothic")
        if font_path is None or (font_path and not Path(font_path).exists()):
            font_path = None
            if sys.platform.startswith("win"):
                font_family = "Malgun Gothic"
            logger.debug(f"레지스트리 폰트 없음, 시스템 폰트 사용: {font_family}")
        else:
            logger.debug(f"레지스트리 폰트 경로: {font_path}")

    # 3. 폰트 파일을 font_manager에 등록
    resolved_font_name: str | None = None
    if font_path:
        try:
            fm.fontManager.addfont(font_path)
            fp = fm.FontProperties(fname=font_path)
            resolved_font_name = fp.get_name()
            logger.debug(f"폰트 파일 등록: {resolved_font_name} ({font_path})")
        except Exception as e:
            logger.debug(f"폰트 파일 등록 실패: {e}")

    # 4. findfont 내부 캐시 무효화 (핵심)
    # matplotlib는 findfont() 결과를 LRU 캐시에 저장하므로
    # addfont() 후에도 캐시가 살아있으면 구 폰트가 반환됨
    _cleared = False
    # matplotlib 3.5+ : FontManager._findfont_cached
    if hasattr(fm.fontManager, "_findfont_cached"):
        try:
            fm.fontManager._findfont_cached.cache_clear()
            _cleared = True
            logger.debug("findfont 캐시 무효화: _findfont_cached.cache_clear()")
        except Exception:
            pass
    # 대안: fontManager 인스턴스 교체 (font 목록은 유지)
    if not _cleared:
        try:
            # ttflist를 보존하며 fontManager만 재초기화
            ttflist_backup = list(fm.fontManager.ttflist)
            fm.fontManager.__init__()
            # 백업된 폰트 목록 중 새로 추가된 항목 재삽입
            existing = {e.fname for e in fm.fontManager.ttflist}
            for entry in ttflist_backup:
                if entry.fname not in existing:
                    fm.fontManager.ttflist.append(entry)
            logger.debug("fontManager 재초기화로 캐시 무효화")
        except Exception as e:
            logger.debug(f"fontManager 재초기화 실패: {e}")

    # 5. rcParams 적용
    target_family = resolved_font_name or font_family or "NanumGothic"
    matplotlib.rcParams["font.family"] = target_family
    for key, value in default_kwargs.items():
        matplotlib.rcParams[key] = value

    logger.debug(f"설정된 폰트 패밀리: {matplotlib.rcParams['font.family']}")

    set_preferred(font_path, target_family, default_kwargs)
    patch_rcparams_setitem()

    return plt


def matplotlib_font_set(
    font_family: str | None = None, font_path: str | None = None, **kwargs: Any
) -> str | None:
    """matplotlib_font_reset를 호출하지 않고 선호 폰트만 등록 (즉시 적용).

    Parameters
    ----------
    font_family : str, optional
        사용할 폰트 패밀리 이름
    font_path : str, optional
        폰트 파일 경로
    **kwargs
        matplotlib rcParams에 전달할 추가 설정

    Returns
    -------
    str | None
        적용된 폰트 패밀리 이름
    """
    default_kwargs: dict = {"axes.unicode_minus": False, "font.size": 10}
    default_kwargs.update(kwargs)

    if font_path is None and font_family is None:
        font_family = "NanumGothic"
        font_path = matplotlib_font_resource.path_of("NanumGothic")
        if font_path is None or (font_path and not Path(font_path).exists()):
            font_path = None
            if sys.platform.startswith("win"):
                font_family = "Malgun Gothic"
            logger.debug(f"레지스트리 폰트 없음, 시스템 폰트 사용: {font_family}")
        else:
            logger.debug(f"레지스트리 폰트 경로: {font_path}")

    set_preferred(font_path, font_family, default_kwargs)
    patch_rcparams_setitem()

    return font_family


def matplotlib_font_get() -> dict[str, str | None]:
    """현재 설정된 폰트 정보 반환.

    설정되기 전이라도 한글 폰트의 절대 경로를 자동 탐색하여 반환합니다.

    Returns
    -------
    dict[str, str | None]
        - 'font_family': 폰트 패밀리 이름
        - 'font_path': 폰트 파일 절대 경로 (없으면 None)

    Notes
    -----
    반환된 font_path는 matplotlib 내에서 사용하기에 안전합니다.
    다른 라이브러리(PIL, reportlab 등)에서 사용 시 주의사항:

    - **개발 환경**: 로컬 파일 경로이므로 안전하게 사용 가능
    - **pip 설치 환경**: 일반적으로 안전하게 사용 가능
    - **ZIP 배포 환경**: 경로가 일시적일 수 있으므로 즉시 사용 권장

    Examples
    --------
    >>> font_info = matplotlib_font_get()
    >>> print(font_info['font_family'])
    'NanumGothic'
    >>> print(font_info['font_path'])
    'd:\\\\...\\\\fonts\\\\NanumGothic.ttf'
    """
    font_path, font_family, _ = get_preferred()

    if font_path is None and font_family is None:
        font_family = "NanumGothic"
        font_path = matplotlib_font_resource.path_of("NanumGothic")
        if font_path is None or (font_path and not Path(font_path).exists()):
            font_path = None
            if sys.platform.startswith("win"):
                font_family = "Malgun Gothic"
            logger.debug(f"레지스트리 폰트 없음, 시스템 폰트 사용: {font_family}")

    return {"font_family": font_family, "font_path": font_path}


# 패키지 폰트 일괄 등록 (import 시점)
matplotlib_font_resource.load_all()

# 환경별 자동 초기화
try:
    if is_jupyter_environment():
        matplotlib_font_reset()
        logger.info("Jupyter/IPython 환경 감지: matplotlib_font_reset() 실행")
    else:
        _family = matplotlib_font_set()
        logger.info(f"matplotlib_font_set() 폰트: {_family}")
except Exception:
    pass
