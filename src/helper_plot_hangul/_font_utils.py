"""내부 폰트 유틸리티: rcParams 재적용 및 matplotlib.style.use 패치."""

from helper_plot_hangul._logger import logger

# 선호 폰트 저장소 (helper_plot_hangul 모듈 네임스페이스 대신 이 모듈이 상태 보유)
_preferred_font_path: str | None = None
_preferred_font_family: str | None = None
_preferred_font_kwargs: dict = {}
_style_patched: bool = False


def reapply_font_rcparams() -> None:
    """저장된 선호 폰트를 rcParams에 재적용 (스타일 적용 후 자동 호출)."""
    try:
        import matplotlib.font_manager as fm
        import matplotlib.pyplot as _plt

        font_path = _preferred_font_path
        font_family = _preferred_font_family
        kwargs = _preferred_font_kwargs

        if font_path:
            try:
                fm.fontManager.addfont(font_path)
                fp = fm.FontProperties(fname=font_path)
                font_name = fp.get_name()
                _plt.rcParams["font.family"] = font_name
                logger.debug(f"폰트 재적용: {font_name} (경로: {font_path})")
            except Exception as e:
                logger.debug(f"폰트 경로 재적용 실패: {e}")
                if font_family:
                    _plt.rcParams["font.family"] = font_family
        elif font_family:
            _plt.rcParams["font.family"] = font_family
            logger.debug(f"폰트 재적용: {font_family}")

        for k, v in kwargs.items():
            _plt.rcParams[k] = v

    except Exception as e:
        logger.debug(f"폰트 재적용 중 예외 발생: {e}")


def set_preferred(
    font_path: str | None,
    font_family: str | None,
    font_kwargs: dict,
) -> None:
    """선호 폰트 정보를 저장하고 rcParams에 즉시 적용."""
    global _preferred_font_path, _preferred_font_family, _preferred_font_kwargs
    _preferred_font_path = font_path
    _preferred_font_family = font_family
    _preferred_font_kwargs = font_kwargs
    reapply_font_rcparams()


def get_preferred() -> tuple[str | None, str | None, dict]:
    """저장된 선호 폰트 정보 반환."""
    return _preferred_font_path, _preferred_font_family, _preferred_font_kwargs


def patch_style_use() -> None:
    """matplotlib.style.use를 패치하여 스타일 적용 후 자동으로 한글 폰트 재설정."""
    global _style_patched
    if _style_patched:
        return
    try:
        import matplotlib.style as mstyle

        _orig_style_use = mstyle.use

        def _patched_style_use(style, *args, **kwargs):
            result = _orig_style_use(style, *args, **kwargs)
            if _preferred_font_path or _preferred_font_family:
                reapply_font_rcparams()
                logger.debug(f"스타일 '{style}' 적용 후 한글 폰트 자동 재설정 완료")
            return result

        mstyle.use = _patched_style_use
        _style_patched = True
        logger.debug("matplotlib.style.use 패치 완료")

    except Exception as e:
        logger.debug(f"matplotlib.style.use 패치 실패 (무시): {e}")
