import logging
import os
import sys
import tarfile
import re
from datetime import datetime
from pathlib import Path


def _archive_old_logs(log_dir: Path, today_str: str):
    pattern = re.compile(r"merchant_auto_settlement_(\d{8})\.log$")

    for log_file in log_dir.glob("*.log"):
        match = pattern.match(log_file.name)
        if not match:
            continue

        log_date = match.group(1)
        if log_date == today_str:
            continue

        tar_path = log_file.with_suffix(".tar.gz")
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(log_file, arcname=log_file.name)

        log_file.unlink()


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        base_dir = Path(__file__).resolve().parent.parent
        log_dir = base_dir / "log"
        log_dir.mkdir(exist_ok=True)

        today_str = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"merchant_auto_settlement_{today_str}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        _archive_old_logs(log_dir, today_str)

    return logger
