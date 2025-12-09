"""
helper-plot-hangul 로컬 설치 및 테스트 스크립트

사용법:
    python test_install.py
"""

import subprocess
import sys
from pathlib import Path


def test_local_install():
    """로컬 패키지 설치 및 테스트"""
    print("=" * 60)
    print("helper-plot-hangul 로컬 설치 테스트")
    print("=" * 60)
    print()
    
    # 1. 현재 디렉토리 확인
    current_dir = Path(__file__).parent
    print(f"📁 현재 디렉토리: {current_dir}")
    print()
    
    # 2. 패키지 설치 (편집 모드)
    print("패키지 설치 중 (편집 모드)...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        cwd=current_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("설치 실패:")
        print(result.stderr)
        sys.exit(1)
    
    print("설치 완료")
    print()
    
    # 3. 임포트 테스트
    print("🧪 임포트 테스트...")
    try:
        from helper_plot_hangul import matplotlib_font_reset, matplotlib_font_set, __version__
        print(f"임포트 성공 (버전: {__version__})")
    except ImportError as e:
        print(f"임포트 실패: {e}")
        sys.exit(1)
    
    print()
    
    # 4. 기본 기능 테스트
    print("🧪 기본 기능 테스트...")
    try:
        plt = matplotlib_font_reset()
        print("matplotlib_font_reset() 성공")
        
        # 간단한 플롯 생성 (표시 안함)
        fig = plt.figure()
        plt.plot([1, 2, 3], [1, 4, 9])
        plt.title('한글 테스트')
        plt.close(fig)
        print("한글 플롯 생성 성공")
    except Exception as e:
        print(f"기능 테스트 실패: {e}")
        sys.exit(1)
    
    print()
    print("모든 테스트 통과!")


if __name__ == "__main__":
    test_local_install()
