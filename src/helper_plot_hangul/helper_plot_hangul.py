import os
import sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import importlib.resources as resources
import inspect
import warnings
from pathlib import Path
from typing import Any
import logging
try:
    import IPython
    from IPython.display import HTML
    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False    
    
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    sh = logging.StreamHandler()
    sh.setLevel(logger.level)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    logger.addHandler(sh)

def matplotlib_font_reset(font_family: str | None = None, font_path: str | None = None, **kwargs: Any) -> Any:
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
    3. 둘 다 없으면 'NanumGothic' 기본값 사용 + 자동 탐색
    """
    
    if isinstance(font_family, (str, bytes, os.PathLike)) and font_family and os.path.exists(font_family):
        font_path = str(font_family)
        font_family = None

    # 기본값 설정
    default_kwargs = {'axes.unicode_minus': False, 'font.size': 10}
    default_kwargs.update(kwargs)
    
    modules_to_remove = [mod for mod in sys.modules if mod.startswith('matplotlib')]
    for mod in modules_to_remove:
        del sys.modules[mod]

    # matplotlib 재임포트
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    # 폰트 캐시 클리어 (중요!)
    try:
        fm._get_fontconfig_fonts.cache_clear()
    except:
        pass
    
    try:
        fm.fontManager.__init__()
    except:
        pass
    
    # font_path가 없고 font_family도 없으면 자동 탐색
    if font_path is None and font_family is None:
        font_family = 'NanumGothic'
        # 1. 개발 환경: 로컬 fonts 폴더 확인
        local_font_path = Path(__file__).parent / "fonts" / "NanumGothic.ttf"
        
        if local_font_path.exists():
            font_path = str(local_font_path)
        else:
            # 2. pip 배포 환경: 패키지 내부 fonts 폴더
            try:
                font_path = str(resources.files("helper_plot_hangul").joinpath("fonts/NanumGothic.ttf"))
            except Exception:
                font_path = None
        logger.debug(f"자동 탐색된 폰트 경로: {font_path}")
    
    # 우선순위: font_path > font_family
    if font_path:
        try:
            fm.fontManager.addfont(font_path)  # matplotlib >= 3.2
            fp = fm.FontProperties(fname=font_path)
            font_name = fp.get_name()
            plt.rcParams['font.family'] = font_name
        except Exception:
            # 실패 시 font_family 사용
            if font_family:
                plt.rcParams['font.family'] = font_family
            else:
                plt.rcParams['font.family'] = 'NanumGothic'
    elif font_family:
        plt.rcParams['font.family'] = font_family
    else:
        plt.rcParams['font.family'] = 'NanumGothic'
    logger.debug(f"설정된 폰트 패밀리: {plt.rcParams['font.family']}")
    
    # 추가 설정 적용
    for key, value in default_kwargs.items():
        plt.rcParams[key] = value
    
    # IPython 환경에서 전역 등록 (Jupyter/Colab 호환성 개선)
    try:
        # IPython/Jupyter 사용자 네임스페이스에 등록
        if IPYTHON_AVAILABLE:
            ipy = IPython.get_ipython()
            if ipy is not None:
                ipy.user_ns["plt"] = plt

        # 호출자 모듈의 전역(namespace)에 plt를 넣어 할당 없이 사용 가능하도록 함
        try:
            caller = inspect.currentframe().f_back
            if caller is not None:
                caller.f_globals["plt"] = plt
        except Exception:
            pass

        # 현재 모듈의 globals에도 보장
        globals()["plt"] = plt
    except Exception:
        globals()["plt"] = plt
    
    # 선호 폰트 정보 저장 (스타일 적용 후 재적용용)
    globals()["_preferred_font_path"] = font_path
    globals()["_preferred_font_family"] = font_family if font_family else plt.rcParams.get('font.family')
    globals()["_preferred_font_kwargs"] = default_kwargs
    
    # matplotlib.style.use 패치 (최초 1회만)
    if not globals().get("_style_patched", False):
        _patch_style_use()
        globals()["_style_patched"] = True
    
    return plt


def _reapply_font_rcparams():
    """모듈에 저장된 선호 폰트를 rcParams에 재적용 (스타일 적용 후 자동 호출)."""
    try:
        import matplotlib.font_manager as fm
        import matplotlib.pyplot as _plt
        
        font_path = globals().get("_preferred_font_path")
        font_family = globals().get("_preferred_font_family")
        kwargs = globals().get("_preferred_font_kwargs", {})

        if font_path:
            try:
                fm.fontManager.addfont(font_path)
                fp = fm.FontProperties(fname=font_path)
                font_name = fp.get_name()
                _plt.rcParams['font.family'] = font_name
                logger.debug(f"폰트 재적용: {font_name} (경로: {font_path})")
            except Exception as e:
                logger.debug(f"폰트 경로 재적용 실패: {e}")
                if font_family:
                    _plt.rcParams['font.family'] = font_family
        elif font_family:
            _plt.rcParams['font.family'] = font_family
            logger.debug(f"폰트 재적용: {font_family}")

        # 기타 저장된 rc 설정 재적용
        for k, v in kwargs.items():
            _plt.rcParams[k] = v
            
    except Exception as e:
        logger.debug(f"폰트 재적용 중 예외 발생: {e}")


def _patch_style_use():
    """matplotlib.style.use를 패치하여 스타일 적용 후 자동으로 한글 폰트 재설정."""
    try:
        import matplotlib.style as mstyle
        _orig_style_use = mstyle.use

        def _patched_style_use(style, *args, **kwargs):
            result = _orig_style_use(style, *args, **kwargs)
            # 스타일 적용 직후 저장된 한글 폰트 재적용
            if globals().get("_preferred_font_path") or globals().get("_preferred_font_family"):
                _reapply_font_rcparams()
                logger.debug(f"스타일 '{style}' 적용 후 한글 폰트 자동 재설정 완료")
            return result

        mstyle.use = _patched_style_use
        logger.debug("matplotlib.style.use 패치 완료")
        
    except Exception as e:
        logger.debug(f"matplotlib.style.use 패치 실패 (무시): {e}")


def matplotlib_font_set(font_family: str | None = None, font_path: str | None = None, **kwargs: Any):
    """matplotlib_font_reset를 호출하지 않고 선호 폰트만 등록 (즉시 적용).
    
    Parameters
    ----------
    font_family : str, optional
        사용할 폰트 패밀리 이름
    font_path : str, optional
        폰트 파일 경로
    **kwargs
        matplotlib rcParams에 전달할 추가 설정
    """
    import matplotlib.pyplot as _plt
    
    default_kwargs = {'axes.unicode_minus': False, 'font.size': 10}
    default_kwargs.update(kwargs)
    
    globals()["_preferred_font_path"] = font_path
    globals()["_preferred_font_family"] = font_family
    globals()["_preferred_font_kwargs"] = default_kwargs
    
    # 현재 세션의 rcParams에도 즉시 적용
    _reapply_font_rcparams()
    
    # 패치 적용
    if not globals().get("_style_patched", False):
        _patch_style_use()
        globals()["_style_patched"] = True


matplotlib_font_reset()

# 예시 사용법
if __name__ == "__main__":
    # plt = matplotlib_font_reset(r'src\helper_plot_hangul\fonts\NanumGothic.ttf')

    # 스타일 적용 테스트 (자동으로 한글 폰트 재설정됨)
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title('한글 폰트 테스트')
    plt.xlabel('X축')
    plt.ylabel('Y축')
    plt.show()