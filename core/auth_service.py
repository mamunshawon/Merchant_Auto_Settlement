import time
from selenium.webdriver.common.by import By
from core.webdriver_manager import create_driver
from config.settings import AUTH_LOGIN_PAGE, USERNAME, PASSWORD
from utils.logger import get_logger

logger = get_logger("AUTH")


class AuthService:

    def login_and_get_cookies(self):
        driver = create_driver()

        try:
            driver.get(AUTH_LOGIN_PAGE)

            # Adjust selectors if needed
            driver.find_element(By.NAME, "username").send_keys(USERNAME)
            driver.find_element(By.NAME, "password").send_keys(PASSWORD)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()

            time.sleep(5)  # Replace with WebDriverWait later

            cookies = driver.get_cookies()

            logger.info("Login successful via Selenium")

            return cookies

        finally:
            driver.quit()
