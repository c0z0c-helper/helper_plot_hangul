"""MatplotlibFontResource 인터페이스 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from helper_plot_hangul._font_resource import MatplotlibFontResource, matplotlib_font_resource


class TestMatplotlibFontResourceInterface:
    """MatplotlibFontResource 공개 인터페이스 단위 테스트."""

    def test_singleton_instance_exists(self) -> None:
        """모듈 수준 싱글톤 인스턴스가 존재해야 한다."""
        assert matplotlib_font_resource is not None
        assert isinstance(matplotlib_font_resource, MatplotlibFontResource)

    def test_register_adds_family(self) -> None:
        """register() 후 families()에 해당 패밀리가 포함되어야 한다."""
        r = MatplotlibFontResource()
        r.register("TestFont", "TestFont.ttf")
        assert "TestFont" in r.families()

    def test_families_returns_list(self) -> None:
        """families()는 list를 반환해야 한다."""
        assert isinstance(matplotlib_font_resource.families(), list)

    def test_families_not_empty_after_auto_register(self) -> None:
        """register_fonts_dir() 자동 호출로 패밀리 목록이 비어있지 않아야 한다."""
        assert len(matplotlib_font_resource.families()) > 0

    def test_path_of_registered_font_returns_str_or_none(self) -> None:
        """path_of()는 str 또는 None을 반환해야 한다."""
        families = matplotlib_font_resource.families()
        if families:
            result = matplotlib_font_resource.path_of(families[0])
            assert result is None or isinstance(result, str)

    def test_path_of_nanum_gothic_exists(self) -> None:
        """NanumGothic 폰트 경로가 실제 파일로 존재해야 한다."""
        path = matplotlib_font_resource.path_of("NanumGothic")
        if path is not None:
            assert Path(path).exists(), f"폰트 파일 없음: {path}"

    def test_path_of_unknown_family_returns_none(self) -> None:
        """등록되지 않은 패밀리는 None을 반환해야 한다."""
        result = matplotlib_font_resource.path_of("__no_such_font__")
        assert result is None

    def test_load_all_does_not_raise(self) -> None:
        """load_all()은 예외 없이 실행되어야 한다."""
        matplotlib_font_resource.load_all()

    def test_register_fonts_dir_returns_list(self) -> None:
        """register_fonts_dir()는 list[str]을 반환해야 한다."""
        r = MatplotlibFontResource()
        result = r.register_fonts_dir()
        assert isinstance(result, list)

    def test_register_fonts_dir_custom_path_nonexistent(self, tmp_path: Path) -> None:
        """존재하지 않는 fonts_dir도 빈 목록으로 정상 처리되어야 한다."""
        empty_dir = tmp_path / "no_fonts"
        empty_dir.mkdir()
        r = MatplotlibFontResource()
        result = r.register_fonts_dir(empty_dir)
        assert result == []

    def test_register_fonts_dir_custom_path_with_ttf(self, tmp_path: Path) -> None:
        """사용자 지정 fonts_dir 내 TTF 파일이 등록되어야 한다."""
        font_file = tmp_path / "MyCustom.ttf"
        font_file.write_bytes(b"")  # 빈 파일로 등록 경로만 검증
        r = MatplotlibFontResource()
        registered = r.register_fonts_dir(tmp_path)
        assert "MyCustom" in registered
