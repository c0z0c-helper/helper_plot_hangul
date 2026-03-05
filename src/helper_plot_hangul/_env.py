"""실행 환경 감지 유틸리티."""


def is_jupyter_environment() -> bool:
    """Jupyter/IPython 환경 여부 확인."""
    try:
        get_ipython()  # type: ignore
        return True
    except (NameError, Exception):
        return False


def is_streamlit_environment() -> bool:
    """Streamlit 환경 여부 확인."""
    try:
        import streamlit.runtime.scriptrunner.script_run_context as ctx

        return ctx.get_script_run_ctx() is not None
    except Exception:
        return False
