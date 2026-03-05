import logging

logger = logging.getLogger("helper_plot_hangul")
logger.setLevel(logging.WARNING)
if not logger.handlers:
    sh = logging.StreamHandler()
    sh.setLevel(logger.level)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    logger.addHandler(sh)
