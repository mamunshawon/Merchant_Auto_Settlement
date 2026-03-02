from ftplib import FTP
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("FTP_CLIENT")


class FTPClient:
    def __init__(self, host, port, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ftp = None

    def connect(self):
        """Establish FTP connection"""
        try:
            logger.info(f"Attempting FTP connection to {self.host}:{self.port}")
            self.ftp = FTP()
            self.ftp.set_debuglevel(2)  # Enable debug output
            
            logger.info(f"Connecting to {self.host}:{self.port} with timeout 60 seconds")
            self.ftp.connect(self.host, self.port, timeout=60)
            
            logger.info(f"Connected to FTP server {self.host}:{self.port}")
            logger.info(f"FTP response: {self.ftp.welcome}")
            
            if self.username and self.password:
                logger.info(f"Logging in as {self.username}")
                response = self.ftp.login(self.username, self.password)
                logger.info(f"Login response: {response}")
            else:
                logger.info("Attempting anonymous login")
                response = self.ftp.login()
                logger.info(f"Anonymous login response: {response}")
                
            logger.info(f"Successfully authenticated to FTP server {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"FTP connection failed: {e}")
            logger.error(f"Host: {self.host}, Port: {self.port}, Username: {self.username}")
            raise

    def disconnect(self):
        """Close FTP connection"""
        try:
            if self.ftp:
                self.ftp.quit()
                logger.info("Disconnected from FTP server")
        except Exception as e:
            logger.error(f"FTP disconnection error: {e}")

    def fetch_file(self, remote_dir, filename, local_path):
        """Fetch a file from FTP server"""
        try:
            self.ftp.cwd(remote_dir)
            logger.info(f"Changed to remote directory: {remote_dir}")

            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {filename}', f.write)
            logger.info(f"Downloaded {filename} to {local_path}")
        except Exception as e:
            logger.error(f"File download failed: {e}")
            raise

    def fetch_latest_settlement_report(self, remote_dir, local_path):
        """
        Fetch the latest auto settlement report file from FTP.
        Expects filename format: auto_settle_failure_report_YYYYMMDD.xlsx
        """
        try:
            self.ftp.cwd(remote_dir)
            logger.info(f"Listing files in {remote_dir}")

            file_list = self.ftp.nlst()
            
            # Filter for settlement report files
            settlement_files = [
                f for f in file_list 
                if f.startswith("auto_settle_failure_report_") and f.endswith(".xlsx")
            ]

            if not settlement_files:
                raise Exception("No settlement report files found in FTP server")

            # Get the latest file (sorted by date in filename)
            latest_file = sorted(settlement_files)[-1]
            logger.info(f"Found settlement report file: {latest_file}")

            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {latest_file}', f.write)
            
            logger.info(f"Downloaded {latest_file} to {local_path}")
            return latest_file

        except Exception as e:
            logger.error(f"Failed to fetch settlement report: {e}")
            raise
