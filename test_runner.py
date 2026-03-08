from datetime import datetime

import pandas as pd

from core.session_manager import SessionManager
from services.auto_settlement_service import AutoSettlementService
from services.data_processor import DataProcessor
from services.email_service import EmailService
from services.report_service import ReportService
from config.settings import EMAIL_SENDER, EMAIL_RECEIVER, SMTP_SERVER, SMTP_PORT
from main import process_merchant
from utils.logger import get_logger


TEST_MERCHANT_ID = "BM00RZSX00261"
TEST_QR_MERCHANT_ID = "BM00RZSX00261"

logger = get_logger("TEST_RUNNER")


def main():
    logger.info(f"Starting test run for merchant {TEST_MERCHANT_ID}")

    df = pd.DataFrame(
        [
            {
                "MERCHANT_ID": TEST_MERCHANT_ID,
                "HOUR": 10,
                "MINUTE": 0,
            }
        ]
    )

    merchant_list = DataProcessor.process_merchant_data(df)
    qr_df = pd.DataFrame(
        [
            {
                "MERCHANT_ID": TEST_QR_MERCHANT_ID,
                "HOUR": 10,
                "MINUTE": 15,
            }
        ]
    )
    qr_merchant_list = DataProcessor.process_merchant_data(qr_df)

    session_manager = SessionManager()
    auto_service = AutoSettlementService(session_manager)
    report_service = ReportService()
    qr_report_service = ReportService()

    for merchant in merchant_list:
        (
            merchant_id,
            old_hour,
            old_minute,
            new_hour,
            new_minute,
            status,
            message,
        ) = process_merchant(auto_service, merchant)

        report_service.add_record(
            merchant_id,
            old_hour,
            old_minute,
            new_hour,
            new_minute,
            status,
            message,
        )

    for merchant in qr_merchant_list:
        (
            merchant_id,
            old_hour,
            old_minute,
            new_hour,
            new_minute,
            status,
            message,
        ) = process_merchant(auto_service, merchant)

        qr_report_service.add_record(
            merchant_id,
            old_hour,
            old_minute,
            new_hour,
            new_minute,
            status,
            message,
        )

    report_file = report_service.save()
    qr_report_file = qr_report_service.save()
    logger.info("Test merchant processed successfully")

    total_merchants = len(merchant_list)
    success_count = sum(
        1 for row in report_service.rows if row.get("status") == "SUCCESS"
    )
    total_qr_merchants = len(qr_merchant_list)
    qr_success_count = sum(
        1 for row in qr_report_service.rows if row.get("status") == "SUCCESS"
    )

    email_service = EmailService(
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        sender=EMAIL_SENDER,
        receiver=EMAIL_RECEIVER,
    )
    email_service.send_reports(
        [report_file, qr_report_file],
        subject=f"[TEST] Auto Settlement Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        body=(
            f"[TEST RUN]\n"
            f"Merchant Auto Settlement Refresh count: {success_count}/{total_merchants}\n"
            f"QR Merchant Auto Settlement Refresh count: {qr_success_count}/{total_qr_merchants}\n\n"
            f"Please find the auto settlement report attached."
        ),
    )

    logger.info("Test run completed")


if __name__ == "__main__":
    main()

