"""pytest conftest: 테스트 결과를 reports/YYYYMMDD_HHMMSS.md 로 저장."""

from __future__ import annotations
import pytest
from typing import Any
from pathlib import Path
from datetime import datetime
import os

# 디스플레이 없는 환경(CI/pytest)에서 Tk 백엔드 오류 방지
# matplotlib import 전에 반드시 설정해야 함
import matplotlib
matplotlib.use("Agg")


# ---------------------------------------------------------------------------
# 결과 수집 훅
# ---------------------------------------------------------------------------

_results: list[dict[str, Any]] = []
_session_start: datetime = datetime.now()


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """각 테스트 단계(setup/call/teardown) 결과 수집."""
    if report.when != "call":
        return

    if report.passed:
        status = "PASS"
    elif report.failed:
        status = "FAIL"
    else:
        status = "SKIP"

    # nodeid 예: tests/test_public_api.py::TestMatplotlibFontReset::test_returns_pyplot
    parts = report.nodeid.split("::")
    module = parts[0] if len(parts) >= 1 else ""
    test_name = "::".join(parts[1:]) if len(parts) >= 2 else report.nodeid

    error_msg = ""
    if report.failed and report.longrepr:
        lines = str(report.longrepr).strip().splitlines()
        # 마지막 의미 있는 줄만 요약
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith("_"):
                error_msg = line[:120]
                break

    _results.append(
        {
            "module": module,
            "test": test_name,
            "status": status,
            "duration": f"{report.duration:.3f}s",
            "error": error_msg,
        }
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """세션 종료 시 reports/ 폴더에 MD 파일 작성."""
    if not _results:
        return

    repo_root = Path(__file__).resolve().parents[1]
    reports_dir = repo_root / "reports"
    reports_dir.mkdir(exist_ok=True)

    timestamp = _session_start.strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"{timestamp}.md"

    total = len(_results)
    passed = sum(1 for r in _results if r["status"] == "PASS")
    failed = sum(1 for r in _results if r["status"] == "FAIL")
    skipped = sum(1 for r in _results if r["status"] == "SKIP")
    duration_total = _session_start  # 시작 시각은 이미 캡처됨

    lines: list[str] = []
    lines.append(f"# 테스트 리포트")
    lines.append(f"")
    lines.append(f"- 실행 일시: {_session_start.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(
        f"- 총 테스트: {total}  |  PASS: {passed}  |  FAIL: {failed}  |  SKIP: {skipped}")
    lines.append(f"")

    # 모듈별 그룹핑
    modules: dict[str, list[dict]] = {}
    for r in _results:
        modules.setdefault(r["module"], []).append(r)

    for mod, rows in modules.items():
        mod_pass = sum(1 for r in rows if r["status"] == "PASS")
        mod_fail = sum(1 for r in rows if r["status"] == "FAIL")
        lines.append(f"## {mod}  (PASS {mod_pass} / FAIL {mod_fail})")
        lines.append(f"")
        lines.append(f"| # | 테스트 | 상태 | 시간 | 오류 요약 |")
        lines.append(f"|---|--------|------|------|-----------|")
        for i, r in enumerate(rows, 1):
            status_icon = "✅" if r["status"] == "PASS" else (
                "❌" if r["status"] == "FAIL" else "⏭️")
            error_col = r["error"].replace("|", "\\|") if r["error"] else "-"
            lines.append(
                f"| {i} | `{r['test']}` | {status_icon} {r['status']} | {r['duration']} | {error_col} |"
            )
        lines.append(f"")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[report] {report_path}")
