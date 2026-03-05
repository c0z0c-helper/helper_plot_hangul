import importlib.resources as resources
import sys
from pathlib import Path

from helper_plot_hangul._logger import logger


class MatplotlibFontResource:
    """패키지 동봉 폰트의 family-path 매핑 레지스트리.

    register() 로 폰트를 등록하고 load_all() 로 matplotlib fontManager에 일괄 등록합니다.
    모듈 임포트 시 자동으로 load_all()이 호출되므로, 등록된 폰트는
    plt.rc('font', family='...') 로 바로 사용할 수 있습니다.

    Examples
    --------
    >>> matplotlib_font_resource.register('MyFont', 'MyFont.ttf')
    >>> matplotlib_font_resource.load_all()
    >>> import matplotlib.pyplot as plt
    >>> plt.rc('font', family='MyFont')
    """

    def __init__(self) -> None:
        # {family_name: ttf_filename} 매핑
        self._registry: dict[str, str] = {}
        # {family_name: resolved_absolute_path}
        self._resolved: dict[str, str] = {}
        # ZIP 배포 환경에서 컨텍스트 수명 유지
        self._contexts: list = []

    def register(self, family: str, ttf_filename: str) -> None:
        """폰트 패밀리 이름과 TTF 파일명을 레지스트리에 등록.

        Parameters
        ----------
        family : str
            matplotlib에서 사용할 폰트 패밀리 이름 (예: 'NanumBarunGothic')
        ttf_filename : str
            패키지 fonts/ 폴더 내 TTF 파일명 (예: 'NanumBarunGothic.ttf')
        """
        self._registry[family] = ttf_filename
        self._resolved.pop(family, None)
        logger.debug(f"폰트 등록: {family} -> {ttf_filename}")

    def _resolve_path(self, family: str) -> str | None:
        """등록된 폰트의 실제 파일 경로를 반환 (캐시 우선)."""
        if family in self._resolved:
            p = self._resolved[family]
            if Path(p).exists():
                return p
            self._resolved.pop(family)

        ttf_filename = self._registry.get(family)
        if ttf_filename is None:
            return None

        # 1. 개발 환경: 패키지 소스 fonts/ 폴더
        local_path = Path(__file__).parent / "fonts" / ttf_filename
        if local_path.exists():
            resolved = str(local_path.resolve())
            self._resolved[family] = resolved
            return resolved

        # 2. pip 설치 환경: importlib.resources
        try:
            pkg_path = resources.files("helper_plot_hangul").joinpath(f"fonts/{ttf_filename}")
            ctx = resources.as_file(pkg_path)
            real_path = ctx.__enter__()
            self._contexts.append(ctx)
            resolved = str(real_path.resolve())
            self._resolved[family] = resolved
            return resolved
        except Exception:
            return None

    def load_all(self) -> None:
        """등록된 모든 폰트를 matplotlib fontManager에 addfont로 일괄 등록."""
        import matplotlib.font_manager as _fm

        for family in list(self._registry):
            path = self._resolve_path(family)
            if path:
                _fm.fontManager.addfont(path)
                logger.debug(f"fontManager 등록 완료: {family} ({path})")
            else:
                logger.warning(f"폰트 파일을 찾을 수 없습니다: {family} ({self._registry[family]})")

    def path_of(self, family: str) -> str | None:
        """등록된 폰트의 절대 경로 반환. 미등록 또는 파일 없으면 None.

        Parameters
        ----------
        family : str
            등록된 폰트 패밀리 이름

        Returns
        -------
        str | None
            폰트 파일 절대 경로
        """
        return self._resolve_path(family)

    def families(self) -> list[str]:
        """등록된 폰트 패밀리 이름 목록 반환."""
        return list(self._registry.keys())

    def register_fonts_dir(self, fonts_dir: str | Path | None = None) -> list[str]:
        """fonts/ 폴더의 TTF 파일을 파일명(확장자 제외)을 family로 자동 등록.

        Parameters
        ----------
        fonts_dir : str | Path | None
            스캔할 폴더 경로. None이면 패키지 동봉 fonts/ 폴더를 사용.

        Returns
        -------
        list[str]
            새로 등록된 폰트 패밀리 이름 목록
        """
        if fonts_dir is None:
            fonts_dir = Path(__file__).parent / "fonts"
        fonts_dir = Path(fonts_dir)

        registered: list[str] = []
        for ttf in sorted(fonts_dir.glob("*.ttf")):
            family = ttf.stem
            self.register(family, ttf.name)
            registered.append(family)

        logger.debug(f"fonts/ 자동 등록 완료: {registered}")
        return registered


# 기본 레지스트리 인스턴스 — fonts/ 폴더 TTF 파일 자동 등록
matplotlib_font_resource = MatplotlibFontResource()
matplotlib_font_resource.register_fonts_dir()
