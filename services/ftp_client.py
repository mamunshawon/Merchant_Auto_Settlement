import pysftp
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("SFTP_CLIENT")


class FTPClient:
    """SFTP Client for fetching files from SFTP server (SSH File Transfer Protocol)"""
    
    def __init__(self, host, port, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sftp = None

    def connect(self):
        """Establish SFTP connection"""
        try:
            logger.info(f"Attempting SFTP connection to {self.host}:{self.port}")
            logger.info(f"Username: {self.username if self.username else 'Anonymous'}")
            
            # SFTP connection options
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None  # Ignore host key checking (use with caution in production)
            
            logger.info(f"Connecting to {self.host}:{self.port} with timeout 60 seconds")
            self.sftp = pysftp.Connection(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                cnopts=cnopts,
                default_path='/'
            )
            
            logger.info(f"✓ SFTP connection established to {self.host}:{self.port}")
            logger.info(f"✓ Successfully authenticated as {self.username}")
            
        except Exception as e:
            logger.error(f"✗ SFTP connection failed: {e}")
            logger.error(f"  Host: {self.host}, Port: {self.port}, Username: {self.username}")
            raise

    def disconnect(self):
        """Close SFTP connection"""
        try:
            if self.sftp:
                self.sftp.close()
                logger.info("✓ Disconnected from SFTP server")
        except Exception as e:
            logger.error(f"SFTP disconnection error: {e}")

    def fetch_file(self, remote_dir, filename, local_path):
        """Fetch a file from SFTP server"""
        try:
            self.sftp.cwd(remote_dir)
            logger.info(f"Changed to remote directory: {remote_dir}")

            remote_file_path = f"{remote_dir}/{filename}"
            logger.info(f"Downloading {filename} from {remote_file_path}")
            
            self.sftp.get(remote_file_path, local_path)
            logger.info(f"✓ Downloaded {filename} to {local_path}")
            
        except Exception as e:
            logger.error(f"✗ File download failed: {e}")
            raise

    def fetch_latest_settlement_report(self, remote_dir, local_path):
        """
        Fetch the latest auto settlement report file from SFTP.
        Expects filename format: auto_settle_failure_report_YYYYMMDD.xlsx
        """
        try:
            self.sftp.cwd(remote_dir)
            logger.info(f"Changed to directory: {remote_dir}")
            logger.info(f"Listing files in {remote_dir}...")

            file_list = self.sftp.listdir()
            logger.info(f"Found {len(file_list)} items in directory")
            
            # Filter for settlement report files
            settlement_files = [
                f for f in file_list 
                if f.startswith("auto_settle_failure_report_") and f.endswith(".xlsx")
            ]

            if not settlement_files:
                logger.error(f"No settlement report files found in {remote_dir}")
                logger.error(f"Available files: {file_list[:10]}")
                raise Exception("No settlement report files found in SFTP server")

            # Get the latest file (sorted by date in filename)
            latest_file = sorted(settlement_files)[-1]
            logger.info(f"✓ Found latest settlement report: {latest_file}")

            remote_file_path = f"{remote_dir}/{latest_file}"
            logger.info(f"Downloading {latest_file} to {local_path}")
            
            self.sftp.get(remote_file_path, local_path)
            
            logger.info(f"✓ Successfully downloaded {latest_file} to {local_path}")
            return latest_file

        except Exception as e:
            logger.error(f"✗ Failed to fetch settlement report: {e}")
            raise

    def fetch_latest_qr_settlement_report(self, remote_dir, local_path):
        """
        Fetch the latest QR auto settlement report file from SFTP.
        Expects filename format: MC_AUTO_SETTLEMENT_FAIL_QR_YYYYMMDD.xlsx
        """
        try:
            self.sftp.cwd(remote_dir)
            logger.info(f"Changed to directory: {remote_dir}")
            logger.info(f"Listing files in {remote_dir}...")

            file_list = self.sftp.listdir()
            logger.info(f"Found {len(file_list)} items in directory")

            qr_files = [
                f for f in file_list
                if f.startswith("MC_AUTO_SETTLEMENT_FAIL_QR_") and f.endswith(".xlsx")
            ]

            if not qr_files:
                raise FileNotFoundError(
                    "No QR settlement report files found in SFTP server"
                )

            latest_file = sorted(qr_files)[-1]
            logger.info(f"✓ Found latest QR settlement report: {latest_file}")

            remote_file_path = f"{remote_dir}/{latest_file}"
            logger.info(f"Downloading {latest_file} to {local_path}")

            self.sftp.get(remote_file_path, local_path)
            logger.info(f"✓ Successfully downloaded {latest_file} to {local_path}")
            return latest_file

        except Exception as e:
            logger.error(f"✗ Failed to fetch QR settlement report: {e}")
            raise
