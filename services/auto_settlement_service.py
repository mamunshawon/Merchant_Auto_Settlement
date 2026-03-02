from config.settings import AUTO_SETTLEMENT_URL
from utils.logger import get_logger

logger = get_logger("AUTO_SETTLEMENT")


class AutoSettlementService:

    def __init__(self, session_manager):
        self.session_manager = session_manager

    def fetch_config(self, merchant_id):
        url = f"{AUTO_SETTLEMENT_URL}?merchantId={merchant_id}"

        response = self.session_manager.request("GET", url)

        if response.status_code != 200:
            raise Exception(f"GET failed: {response.status_code}")

        logger.info(f"Fetched config for {merchant_id}")
        return response.json()

    def update_config(self, merchant_id, base_config, hour, minute):
        url = f"{AUTO_SETTLEMENT_URL}?merchantId={merchant_id}"

        payload = {
            "settlementPolicy": base_config.get("settlementPolicy"),
            "autoSettlementBankAccount": base_config.get("autoSettlementBankAccount"),
            "hour": str(hour),
            "minute": str(minute),
            "range": base_config.get("range"),
            "dayOfWeek": base_config.get("dayOfWeek"),
            "dateOfMonth": base_config.get("dateOfMonth")
        }

        response = self.session_manager.request("PUT", url, json=payload)

        if response.status_code not in [200, 204]:
            raise Exception(f"Update failed: {response.status_code}")

        logger.info(f"Updated merchant {merchant_id}")
