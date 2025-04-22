# logging_config.py
import pytz
import logging
from datetime import datetime
import sys
import logging.handlers
# from contextvars import ContextVar
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

# client_ip_var = ContextVar("client_ip", default="")
# user_id_var = ContextVar("user_id", default="")


def configure_logging(fpath):
    fname = fpath.split('/')[-1]
    logdir = fpath.replace(fname, '')    # 로그 포맷 설정
    log_format = "{asctime} {levelname} | {name} |==> {message}"
    date_format = "%m-%d %H:%M:%S"

    # 로거 초기화
    logger = logging.getLogger(fname)
    # 로그 레벨 설정
    logger.setLevel(logging.INFO)

    # 로그 파일 핸들러 설정
    file_handler = logging.handlers.RotatingFileHandler(logdir + "run.log", maxBytes=10 * 1024 * 1024, backupCount=10, encoding='utf-8')
    formatter = logging.Formatter(log_format, datefmt=date_format, style='{')
    file_handler.setFormatter(formatter)

    # 로그 필터 추가 (client_ip 설정)

    # class ClientInfoFilter(logging.Filter):
    #     def filter(self, record: logging.LogRecord) -> bool:
    #         record.client_ip = client_ip_var.get()
    #         record.user_id = user_id_var.get()
    #         return True

    # logger.addFilter(ClientInfoFilter())

    # 핸들러 추가
    logger.addHandler(file_handler)
    return logger
