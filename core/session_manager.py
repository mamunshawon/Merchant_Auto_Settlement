import requests
import urllib3
from config.settings import VERIFY_SSL
from utils.logger import get_logger
from core.auth_service import AuthService


urllib3.disable_warnings()

logger = get_logger("SESSION")


class SessionManager:

    def __init__(self):
        self.session = requests.Session()
        self.session.verify = VERIFY_SSL
        self.auth_service = AuthService()  # ✅ instantiate
        self.restore_session()

    def restore_session(self):
        logger.info("Restoring session via Selenium login...")

        # ✅ Correct method call
        cookies = self.auth_service.login_and_get_cookies()

        self.session.cookies.clear()

        for cookie in cookies:
            self.session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain")
            )

        logger.info("Session restored successfully")

    def request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)

        # Session expiry detection
        if response.status_code in [401, 403] or "login" in response.text.lower():
            logger.warning("Session expired. Re-authenticating...")
            self.restore_session()
            response = self.session.request(method, url, **kwargs)

        return response
