"""내부 폰트 유틸리티: rcParams 재적용 및 matplotlib 기본값 오버라이드."""

from helper_plot_hangul._logger import logger

# 선호 폰트 저장소 (helper_plot_hangul 모듈 네임스페이스 대신 이 모듈이 상태 보유)
_preferred_font_path: str | None = None
_preferred_font_family: str | None = None
_preferred_font_kwargs: dict = {}
_rcparams_patched: bool = False
_style_patched: bool = False

# CSS generic font family: 이 값으로 font.family를 설정하려는 시도를 차단
_GENERIC_FONT_FAMILIES: frozenset[str] = frozenset(
    {"sans-serif", "serif", "monospace", "cursive", "fantasy"}
)


def patch_rcparams_default(font_family: str, extra: dict) -> None:
    """matplotlib.rcParamsDefault 자체에 한글 폰트를 등록.

    seaborn/matplotlib의 모든 리셋 함수(sns.reset_defaults, sns.set_theme,
    plt.rcdefaults, mpl.rcParams.update(rcParamsDefault) 등)는 내부적으로
    rcParamsDefault를 참조합니다. 기본값 딕셔너리를 직접 수정하면
    어떤 리셋 경로를 통해도 한글 폰트가 유지됩니다.
    """
    try:
        import matplotlib as mpl

        mpl.rcParamsDefault["font.family"] = font_family
        for k, v in extra.items():
            if k in mpl.rcParamsDefault:
                mpl.rcParamsDefault[k] = v
        logger.debug(f"rcParamsDefault 오버라이드 완료: font.family={font_family}")
    except Exception as e:
        logger.debug(f"rcParamsDefault 오버라이드 실패: {e}")


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
    """선호 폰트 정보를 저장하고, rcParams 및 rcParamsDefault에 즉시 적용."""
    global _preferred_font_path, _preferred_font_family, _preferred_font_kwargs
    _preferred_font_path = font_path
    _preferred_font_family = font_family
    _preferred_font_kwargs = font_kwargs
    if font_family:
        patch_rcparams_default(font_family, font_kwargs)
    reapply_font_rcparams()


def get_preferred() -> tuple[str | None, str | None, dict]:
    """저장된 선호 폰트 정보 반환."""
    return _preferred_font_path, _preferred_font_family, _preferred_font_kwargs


def patch_rcparams_setitem() -> None:
    """matplotlib.RcParams.__setitem__을 패치하여 font.family 강제 덮어쓰기를 차단.

    seaborn.set_theme, seaborn.set_style, matplotlib.style.use 등 모든 경로에서
    font.family를 CSS generic family("sans-serif", "serif" 등)로 리셋하려는 시도를
    클래스 레벨 단일 진입점에서 차단합니다.

    개별 함수 래퍼(patch_style_use, patch_seaborn_set_theme)를 대체하므로
    seaborn/matplotlib의 API가 변경되거나 내부 호출 경로가 바뀌어도 영향을 받지
    않습니다. 사용자가 명시적으로 특정 폰트(비 generic)를 지정한 경우에는
    개입하지 않습니다.
    """
    global _rcparams_patched
    if _rcparams_patched:
        return
    try:
        import matplotlib as mpl

        _orig_setitem = mpl.RcParams.__setitem__

        def _guarded_setitem(self, key: str, val) -> None:
            if key == "font.family" and _preferred_font_family:
                # matplotlib 내부에서 val을 list로 전달하는 경우도 있음
                candidate = val[0] if isinstance(val, list) else val
                if candidate in _GENERIC_FONT_FAMILIES:
                    logger.debug(
                        f"font.family='{candidate}' 차단 → '{_preferred_font_family}' 유지"
                    )
                    val = _preferred_font_family
            _orig_setitem(self, key, val)

        mpl.RcParams.__setitem__ = _guarded_setitem
        _rcparams_patched = True
        logger.debug("RcParams.__setitem__ 패치 완료")

    except Exception as e:
        logger.debug(f"RcParams.__setitem__ 패치 실패 (무시): {e}")


def patch_style_use() -> None:
    """matplotlib.style.use를 패치하여 스타일 적용 후 한글 폰트를 자동 재적용.

    ``matplotlib.style.use`` 호출 후 rcParams가 초기화되므로,
    래퍼를 삽입해 ``reapply_font_rcparams``를 자동 호출합니다.
    이미 패치된 경우 재패치하지 않습니다.
    """
    global _style_patched
    if _style_patched:
        return
    try:
        import matplotlib.style as mstyle

        _orig_use = mstyle.use

        def _patched_use(style) -> None:
            _orig_use(style)
            reapply_font_rcparams()
            logger.debug(f"mstyle.use('{style}') 후 폰트 재적용 완료")

        mstyle.use = _patched_use
        _style_patched = True
        logger.debug("matplotlib.style.use 패치 완료")

    except Exception as e:
        logger.debug(f"matplotlib.style.use 패치 실패 (무시): {e}")
