import pandas as pd
from datetime import datetime
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
        filename = f"auto_settlement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df = pd.DataFrame(self.rows)
        df.to_excel(filename, index=False)
        logger.info(f"Report saved: {filename}")
        return filename
