import logging

def setup_logging():
    logger = logging.getLogger()
    log_format = logging.Formatter("%(asctime)-15s %(levelname)-2s %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(log_format)
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)