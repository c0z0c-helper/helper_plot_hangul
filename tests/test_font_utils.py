"""_font_utils 인터페이스 테스트."""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.style as mstyle
import pytest

import helper_plot_hangul._font_utils as fu


class TestGetSetPreferred:
    """get_preferred / set_preferred 단위 테스트."""

    def setup_method(self) -> None:
        """각 테스트 전 상태 초기화."""
        fu._preferred_font_path = None
        fu._preferred_font_family = None
        fu._preferred_font_kwargs = {}

    def test_get_preferred_initial_state(self) -> None:
        """초기 상태는 (None, None, {}) 이어야 한다."""
        path, family, kwargs = fu.get_preferred()
        assert path is None
        assert family is None
        assert kwargs == {}

    def test_set_preferred_stores_values(self) -> None:
        """set_preferred() 이후 get_preferred()로 동일 값을 반환해야 한다."""
        fu.set_preferred(None, "NanumGothic", {"axes.unicode_minus": False})
        path, family, kwargs = fu.get_preferred()
        assert family == "NanumGothic"
        assert kwargs["axes.unicode_minus"] is False

    def test_set_preferred_with_none_family(self) -> None:
        """font_family=None 으로 저장해도 예외 없이 동작해야 한다."""
        fu.set_preferred(None, None, {})
        path, family, kwargs = fu.get_preferred()
        assert path is None
        assert family is None

    def test_set_preferred_applies_rcparams(self) -> None:
        """set_preferred() 호출 후 rcParams에 폰트가 반영되어야 한다."""
        fu.set_preferred(None, "NanumGothic", {"axes.unicode_minus": False})
        assert plt.rcParams.get("font.family") in (
            "NanumGothic",
            ["NanumGothic"],
        )


class TestReapplyFontRcparams:
    """reapply_font_rcparams 단위 테스트."""

    def setup_method(self) -> None:
        fu._preferred_font_path = None
        fu._preferred_font_family = None
        fu._preferred_font_kwargs = {}

    def test_no_preferred_does_not_raise(self) -> None:
        """선호 폰트 미설정 상태에서도 예외 없이 실행되어야 한다."""
        fu.reapply_font_rcparams()

    def test_family_set_applies_to_rcparams(self) -> None:
        """선호 패밀리 설정 후 reapply시 rcParams에 반영되어야 한다."""
        fu._preferred_font_family = "NanumGothic"
        fu._preferred_font_kwargs = {}
        fu.reapply_font_rcparams()
        assert plt.rcParams.get("font.family") in (
            "NanumGothic", ["NanumGothic"])

    def test_extra_rcparams_applied(self) -> None:
        """font_kwargs 내 항목이 rcParams에 적용되어야 한다."""
        fu._preferred_font_family = "NanumGothic"
        fu._preferred_font_kwargs = {"axes.unicode_minus": False}
        fu.reapply_font_rcparams()
        assert plt.rcParams["axes.unicode_minus"] is False


class TestPatchStyleUse:
    """patch_style_use 단위 테스트."""

    def test_patch_is_idempotent(self) -> None:
        """여러 번 호출해도 예외 없이 동작해야 한다."""
        fu._style_patched = False
        fu.patch_style_use()
        fu.patch_style_use()  # 두 번째 호출도 안전해야 함

    def test_style_use_after_patch_does_not_raise(self) -> None:
        """패치 후 mstyle.use() 호출이 예외 없이 실행되어야 한다."""
        fu._style_patched = False
        fu._preferred_font_family = "NanumGothic"
        fu.patch_style_use()
        mstyle.use("default")
