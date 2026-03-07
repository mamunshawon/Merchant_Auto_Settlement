import os
import re
import tarfile
from datetime import datetime
from pathlib import Path

import pandas as pd

from utils.logger import get_logger

logger = get_logger("REPORT")


class ReportService:

    def __init__(self):
        self.rows = []

    def add_record(self, merchant_id, old_hour, old_minute,
                   new_hour, new_minute, status, message):
        self.rows.append({
            "merchantId": merchant_id,
            "oldHour": old_hour,
            "oldMinute": old_minute,
            "newHour": new_hour,
            "newMinute": new_minute,
            "status": status,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def save(self):
        base_dir = Path(__file__).resolve().parent.parent
        reports_dir = base_dir / "report"
        reports_dir.mkdir(exist_ok=True)

        filename = f"auto_settlement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = reports_dir / filename

        df = pd.DataFrame(self.rows)
        df.to_excel(file_path, index=False)
        logger.info(f"Report saved: {file_path}")

        self._archive_old_reports(reports_dir)

        return str(file_path)

    @staticmethod
    def _archive_old_reports(reports_dir: Path):
        today_str = datetime.now().strftime("%Y%m%d")
        pattern = re.compile(r"auto_settlement_report_(\d{8})_\d{6}\.xlsx$")

        for xlsx_path in reports_dir.glob("*.xlsx"):
            match = pattern.match(xlsx_path.name)
            if not match:
                continue

            report_date = match.group(1)
            if report_date == today_str:
                continue

            tar_path = xlsx_path.with_suffix(".tar.gz")
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(xlsx_path, arcname=xlsx_path.name)

            xlsx_path.unlink()
