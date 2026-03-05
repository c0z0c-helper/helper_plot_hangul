"""공개 API: matplotlib 한글 폰트 설정 함수."""

import inspect
import os
import sys
from pathlib import Path
from typing import Any

from helper_plot_hangul._env import is_jupyter_environment, is_streamlit_environment
from helper_plot_hangul._font_resource import matplotlib_font_resource
from helper_plot_hangul._font_utils import (
    get_preferred,
    patch_style_use,
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
    """matplotlib 완전 리셋 (NumPy 호환성 개선).

    matplotlib 모듈을 완전히 리로드하고 한글 폰트를 설정합니다.
    NumPy 2.0+ 호환성을 고려한 안전한 폰트 설정을 수행합니다.

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
        리셋되고 한글 폰트가 설정된 pyplot 모듈.

    Notes
    -----
    폰트 설정 우선순위:
    1. font_path가 있으면 파일에서 폰트 패밀리 이름 추출
    2. font_family만 있으면 해당 이름 사용
    3. 둘 다 없으면 'NanumGothic' 기본값 사용
    """
    if (
        isinstance(font_family, (str, bytes, os.PathLike))
        and font_family
        and os.path.exists(font_family)
    ):
        font_path = str(font_family)
        font_family = None

    default_kwargs: dict = {"axes.unicode_minus": False, "font.size": 10}
    default_kwargs.update(kwargs)

    modules_to_remove = [mod for mod in sys.modules if mod.startswith("matplotlib")]
    for mod in modules_to_remove:
        del sys.modules[mod]

    import matplotlib.font_manager as fm
    import matplotlib.pyplot as plt

    try:
        fm._get_fontconfig_fonts.cache_clear()
    except Exception:
        pass
    try:
        fm.fontManager.__init__()
    except Exception:
        pass

    # 재로드 후 레지스트리 폰트 재등록
    matplotlib_font_resource.load_all()

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

    if font_path:
        try:
            fm.fontManager.addfont(font_path)
            fp = fm.FontProperties(fname=font_path)
            font_name = fp.get_name()
            plt.rcParams["font.family"] = font_name
        except Exception:
            plt.rcParams["font.family"] = font_family if font_family else "NanumGothic"
    elif font_family:
        plt.rcParams["font.family"] = font_family
    else:
        plt.rcParams["font.family"] = "NanumGothic"
    logger.debug(f"설정된 폰트 패밀리: {plt.rcParams['font.family']}")

    for key, value in default_kwargs.items():
        plt.rcParams[key] = value

    # IPython/Jupyter 사용자 네임스페이스에 plt 등록
    try:
        if IPYTHON_AVAILABLE:
            ipy = IPython.get_ipython()
            if ipy is not None:
                ipy.user_ns["plt"] = plt
        try:
            caller = inspect.currentframe().f_back
            if caller is not None:
                caller.f_globals["plt"] = plt
        except Exception:
            pass
        globals()["plt"] = plt
    except Exception:
        globals()["plt"] = plt

    set_preferred(
        font_path, font_family if font_family else plt.rcParams.get("font.family"), default_kwargs
    )
    patch_style_use()

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
    patch_style_use()

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
