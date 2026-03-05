import os
from dotenv import load_dotenv

load_dotenv()

AUTH_LOGIN_PAGE = "https://auth.mynagad.com:10900/authentication-service-provider-1.0/login"
SYS_BASE_URL = "https://sys.mynagad.com:20020"

AUTO_SETTLEMENT_URL = f"{SYS_BASE_URL}/api/merchant/auto-settlement"

USERNAME = os.getenv("NAGAD_USERNAME")
PASSWORD = os.getenv("NAGAD_PASSWORD")

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

# FTP Configuration
FTP_HOST = os.getenv("FTP_HOST", "10.210.10.201")
FTP_PORT = int(os.getenv("FTP_PORT", "40167"))
FTP_USERNAME = os.getenv("FTP_USERNAME")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
FTP_REMOTE_DIR = os.getenv("FTP_REMOTE_DIR", "/home/techops/auto_settlement_report")

VERIFY_SSL = False
HEADLESS = True

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "notification@nagad.com.bd")
# Supports space- or comma-separated list
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "mno.strategy@nagad.com.bd toc@nagad.com.bd")
SMTP_SERVER = os.getenv("SMTP_SERVER", "10.210.10.175")
SMTP_PORT = int(os.getenv("SMTP_PORT", "25"))
