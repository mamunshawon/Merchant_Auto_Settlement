from concurrent.futures import ThreadPoolExecutor, as_completed
from core.session_manager import SessionManager
from services.auto_settlement_service import AutoSettlementService
from services.ftp_client import FTPClient
from services.data_processor import DataProcessor
from services.excel_reader import ExcelReader
from services.report_service import ReportService
from services.email_service import EmailService
from config.settings import (
    FTP_HOST,
    FTP_PORT,
    FTP_USERNAME,
    FTP_PASSWORD,
    FTP_REMOTE_DIR,
    EMAIL_SENDER,
    EMAIL_RECEIVER,
    SMTP_SERVER,
    SMTP_PORT,
)
from utils.logger import get_logger
import pandas as pd
from datetime import datetime

logger = get_logger("MAIN")

EXCEL_FILE = "input.xlsx"


def process_merchant(auto_service, merchant):
    merchant_id = merchant["merchantId"]
    new_hour = merchant["hour"]
    new_minute = merchant["minute"]

    try:
        logger.info(f"Processing {merchant_id}")
        config = auto_service.fetch_config(merchant_id)

        old_hour = config.get("hour")
        old_minute = config.get("minute")

        auto_service.update_config(
            merchant_id,
            config,
            new_hour,
            new_minute
        )

        return (
            merchant_id,
            old_hour,
            old_minute,
            new_hour,
            new_minute,
            "SUCCESS",
            "Updated successfully",
        )

    except Exception as e:
        logger.error(f"Failed for {merchant_id}: {e}")
        return (
            merchant_id,
            None,
            None,
            new_hour,
            new_minute,
            "FAILED",
            str(e),
        )


def main():
    ftp_client = None
    
    try:
        # Step 1: Fetch file from FTP server
        logger.info("Starting FTP file fetch process...")
        ftp_client = FTPClient(FTP_HOST, FTP_PORT, FTP_USERNAME, FTP_PASSWORD)
        ftp_client.connect()
        ftp_client.fetch_latest_settlement_report(FTP_REMOTE_DIR, EXCEL_FILE)
        logger.info(f"Successfully fetched file from FTP: {EXCEL_FILE}")
        
    except Exception as e:
        logger.error(f"FTP fetch failed: {e}")
        raise
    
    finally:
        if ftp_client:
            ftp_client.disconnect()
    
    try:
        # Step 2: Read and process the Excel file
        logger.info(f"Reading and processing data from {EXCEL_FILE}...")
        df = pd.read_excel(EXCEL_FILE)
        
        # Process merchant data: adjust hours and minutes
        merchant_list = DataProcessor.process_merchant_data(df)
        logger.info(f"Processed {len(merchant_list)} merchants from FTP file")
        
        # Step 3: Continue with existing auto-settlement process
        session_manager = SessionManager()
        auto_service = AutoSettlementService(session_manager)
        report_service = ReportService()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_merchant, auto_service, merchant)
                for merchant in merchant_list
            ]

            for future in as_completed(futures):
                (
                    merchant_id,
                    old_hour,
                    old_minute,
                    new_hour,
                    new_minute,
                    status,
                    message,
                ) = future.result()

                report_service.add_record(
                    merchant_id,
                    old_hour,
                    old_minute,
                    new_hour,
                    new_minute,
                    status,
                    message,
                )

        report_file = report_service.save()
        logger.info("All merchants processed successfully")

        email_service = EmailService(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            sender=EMAIL_SENDER,
            receiver=EMAIL_RECEIVER,
        )
        email_service.send_report(
            report_file,
            subject=f"Auto Settlement Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            body="Please find the auto settlement report attached.",
        )
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
