import pandas as pd
from utils.logger import get_logger

logger = get_logger("EXCEL")


class ExcelReader:

    def __init__(self, file_path):
        self.file_path = file_path

    def read_merchants(self):
        try:
            df = pd.read_excel(self.file_path)

            required_columns = {"merchantId", "hour", "minute"}

            if not required_columns.issubset(df.columns):
                raise Exception(f"Excel must contain columns: {required_columns}")

            merchants = []

            for _, row in df.iterrows():
                merchants.append({
                    "merchantId": str(row["merchantId"]).strip(),
                    "hour": int(row["hour"]),
                    "minute": int(row["minute"])
                })

            logger.info(f"Loaded {len(merchants)} merchants from Excel")
            return merchants

        except Exception as e:
            logger.error(f"Excel read failed: {e}")
            raise