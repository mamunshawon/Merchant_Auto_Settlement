import pandas as pd
from utils.logger import get_logger

logger = get_logger("DATA_PROCESSOR")


class DataProcessor:
    """Process merchant data from Excel file"""

    @staticmethod
    def adjust_minute(minute):
        """
        Adjust minute by adding 15 minutes, without changing the hour.
        Logic: 0→15, 15→30, 30→45, 45→0
        Returns: (hour_offset, new_minute) where hour_offset is always 0
        """
        minute = int(minute)
        
        if minute == 0:
            return 0, 15
        elif minute == 15:
            return 0, 30
        elif minute == 30:
            return 0, 45
        elif minute == 45:
            return 0, 0
        else:
            logger.warning(f"Unexpected minute value: {minute}. Valid values are 0, 15, 30, 45")
            # Find closest valid value and adjust
            valid_minutes = [0, 15, 30, 45]
            closest = min(valid_minutes, key=lambda x: abs(x - minute))
            logger.warning(f"Rounding minute from {minute} to {closest}")
            return DataProcessor.adjust_minute(closest)

    @staticmethod
    def process_merchant_data(df):
        """
        Process merchant data: adjust minutes only (hour unchanged).
        
        Expected columns: MERCHANT_ID, HOUR, MINUTE
        Returns processed dataframe with adjusted hours and minutes
        """
        try:
            # Validate required columns
            required_columns = {"MERCHANT_ID", "HOUR", "MINUTE"}
            
            # Check with case insensitivity
            df_columns_upper = [col.upper() for col in df.columns]
            if not required_columns.issubset(set(df_columns_upper)):
                raise Exception(f"Excel must contain columns: {required_columns}")

            # Create a copy to avoid modifying original
            df = df.copy()
            
            # Normalize column names to uppercase for processing
            df.columns = [col.upper() for col in df.columns]

            # Process each merchant
            processed_merchants = []
            for _, row in df.iterrows():
                hour_offset, new_minute = DataProcessor.adjust_minute(row["MINUTE"])
                new_hour = int(row["HOUR"]) + hour_offset
                
                # Handle hour wraparound (24 hour format)
                new_hour = new_hour % 24

                processed_merchants.append({
                    "merchantId": str(row["MERCHANT_ID"]).strip(),
                    "hour": new_hour,
                    "minute": new_minute
                })

            logger.info(f"Processed {len(processed_merchants)} merchants with minute adjustment")
            return processed_merchants

        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise
