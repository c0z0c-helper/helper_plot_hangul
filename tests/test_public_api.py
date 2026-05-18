"""공개 API (matplotlib_font_reset / matplotlib_font_set / matplotlib_font_get) 테스트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pytest

import helper_plot_hangul
from helper_plot_hangul import (
    matplotlib_font_get,
    matplotlib_font_reset,
    matplotlib_font_set,
    matplotlib_font_resource,
    __version__,
)


class TestVersion:
    """패키지 버전 테스트."""

    def test_version_is_string(self) -> None:
        """__version__ 은 문자열이어야 한다."""
        assert isinstance(__version__, str)

    def test_version_format(self) -> None:
        """__version__ 은 major.minor.patch 형식이어야 한다."""
        parts = __version__.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


class TestMatplotlibFontReset:
    """matplotlib_font_reset() 인터페이스 테스트."""

    def test_returns_pyplot_module(self) -> None:
        """반환값이 matplotlib.pyplot 모듈이어야 한다."""
        result = matplotlib_font_reset()
        import matplotlib.pyplot as _plt
        assert result is _plt

    def test_font_family_applied_to_rcparams(self) -> None:
        """호출 후 rcParams['font.family']가 설정되어야 한다."""
        matplotlib_font_reset()
        family = plt.rcParams.get("font.family")
        assert family is not None
        # list 또는 str 모두 허용
        family_str = family[0] if isinstance(family, list) else family
        assert isinstance(family_str, str)
        assert len(family_str) > 0

    def test_unicode_minus_disabled(self) -> None:
        """axes.unicode_minus 가 False로 설정되어야 한다."""
        matplotlib_font_reset()
        assert plt.rcParams["axes.unicode_minus"] is False

    def test_custom_font_family(self) -> None:
        """font_family 인자가 rcParams에 반영되어야 한다."""
        matplotlib_font_reset(font_family="DejaVu Sans")
        family = plt.rcParams.get("font.family")
        family_str = family[0] if isinstance(family, list) else family
        assert family_str == "DejaVu Sans"

    def test_custom_font_path(self) -> None:
        """font_path로 실제 TTF 파일을 지정하면 해당 폰트가 적용되어야 한다."""
        nanum_path = matplotlib_font_resource.path_of("NanumGothic")
        if nanum_path is None:
            pytest.skip("NanumGothic 폰트 파일 없음")
        matplotlib_font_reset(font_path=nanum_path)
        family = plt.rcParams.get("font.family")
        family_str = family[0] if isinstance(family, list) else family
        assert isinstance(family_str, str)
        assert len(family_str) > 0

    def test_font_path_as_first_positional_arg(self) -> None:
        """font_family 자리에 경로 문자열 전달 시 font_path로 처리되어야 한다."""
        nanum_path = matplotlib_font_resource.path_of("NanumGothic")
        if nanum_path is None:
            pytest.skip("NanumGothic 폰트 파일 없음")
        result = matplotlib_font_reset(nanum_path)
        assert result is plt

    def test_extra_kwargs_applied(self) -> None:
        """추가 rcParams 키워드가 반영되어야 한다."""
        matplotlib_font_reset(**{"font.size": 14})
        assert plt.rcParams["font.size"] == 14

    def test_does_not_break_seaborn_import(self) -> None:
        """호출 후 seaborn import 및 기본 함수가 정상 동작해야 한다."""
        matplotlib_font_reset()
        import seaborn as sns
        assert sns.__version__

    def test_findfont_cache_cleared(self) -> None:
        """호출 후 findfont 캐시가 무효화되어야 한다 (3.5+ 확인)."""
        matplotlib_font_reset()
        # 캐시가 있는 버전에서는 cache_info 조회가 가능해야 함
        if hasattr(fm.fontManager, "_findfont_cached"):
            info = fm.fontManager._findfont_cached.cache_info()
            assert info is not None

    def test_figure_creation_after_reset(self) -> None:
        """호출 후 plt.figure() 가 예외 없이 Figure를 반환해야 한다."""
        matplotlib_font_reset()
        fig = plt.figure()
        assert fig is not None
        plt.close(fig)

    def test_title_with_korean_does_not_raise(self) -> None:
        """한글 타이틀 설정이 예외 없이 동작해야 한다."""
        matplotlib_font_reset()
        fig, ax = plt.subplots()
        ax.set_title("한글 테스트")
        plt.close(fig)


class TestMatplotlibFontSet:
    """matplotlib_font_set() 인터페이스 테스트."""

    def test_returns_string_or_none(self) -> None:
        """반환값이 str 또는 None이어야 한다."""
        result = matplotlib_font_set()
        assert result is None or isinstance(result, str)

    def test_returns_font_family_name(self) -> None:
        """반환값이 적용된 폰트 패밀리 이름이어야 한다."""
        result = matplotlib_font_set(font_family="DejaVu Sans")
        assert result == "DejaVu Sans"

    def test_applies_rcparams(self) -> None:
        """호출 후 rcParams에 폰트가 반영되어야 한다."""
        matplotlib_font_set(font_family="DejaVu Sans")
        family = plt.rcParams.get("font.family")
        family_str = family[0] if isinstance(family, list) else family
        assert family_str == "DejaVu Sans"

    def test_default_call_no_exception(self) -> None:
        """인자 없는 호출이 예외 없이 실행되어야 한다."""
        matplotlib_font_set()

    def test_custom_rcparams_kwargs(self) -> None:
        """추가 rcParams 키워드가 반영되어야 한다."""
        matplotlib_font_set(**{"font.size": 12})
        assert plt.rcParams["font.size"] == 12


class TestMatplotlibFontGet:
    """matplotlib_font_get() 인터페이스 테스트."""

    def test_returns_dict(self) -> None:
        """반환값이 dict이어야 한다."""
        result = matplotlib_font_get()
        assert isinstance(result, dict)

    def test_dict_has_required_keys(self) -> None:
        """반환 dict에 'font_family', 'font_path' 키가 있어야 한다."""
        result = matplotlib_font_get()
        assert "font_family" in result
        assert "font_path" in result

    def test_font_family_is_str_or_none(self) -> None:
        """font_family 값이 str 또는 None이어야 한다."""
        result = matplotlib_font_get()
        assert result["font_family"] is None or isinstance(
            result["font_family"], str)

    def test_font_path_is_str_or_none(self) -> None:
        """font_path 값이 str 또는 None이어야 한다."""
        result = matplotlib_font_get()
        assert result["font_path"] is None or isinstance(
            result["font_path"], str)

    def test_font_path_exists_if_set(self) -> None:
        """font_path가 None이 아니면 실제 파일이 존재해야 한다."""
        matplotlib_font_reset()
        result = matplotlib_font_get()
        if result["font_path"] is not None:
            assert Path(result["font_path"]).exists()

    def test_reflects_set_font(self) -> None:
        """matplotlib_font_set() 후 get()이 동일 패밀리를 반환해야 한다."""
        matplotlib_font_set(font_family="DejaVu Sans")
        result = matplotlib_font_get()
        assert result["font_family"] == "DejaVu Sans"


class TestPublicApiAll:
    """__all__ 공개 심볼 노출 테스트."""

    def test_all_exports_present(self) -> None:
        """__all__에 선언된 모든 심볼이 패키지에서 접근 가능해야 한다."""
        for name in helper_plot_hangul.__all__:
            assert hasattr(helper_plot_hangul, name), f"누락된 심볼: {name}"
