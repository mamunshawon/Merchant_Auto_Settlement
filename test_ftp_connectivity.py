#!/usr/bin/env python3
"""
SFTP Connectivity Diagnostic Script
Tests SFTP connection with detailed debugging output
"""

import socket
import pysftp
from config.settings import FTP_HOST, FTP_PORT, FTP_USERNAME, FTP_PASSWORD, FTP_REMOTE_DIR
from utils.logger import get_logger

logger = get_logger("SFTP_DIAGNOSTIC")


def test_network_connectivity():
    """Test basic network connectivity to SFTP server"""
    logger.info("=" * 60)
    logger.info("STEP 1: Testing Network Connectivity")
    logger.info("=" * 60)
    
    try:
        logger.info(f"Attempting socket connection to {FTP_HOST}:{FTP_PORT}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((FTP_HOST, FTP_PORT))
        sock.close()
        
        if result == 0:
            logger.info(f"✓ Network connectivity: SUCCESS - Port {FTP_PORT} is reachable")
            return True
        else:
            logger.error(f"✗ Network connectivity: FAILED - Cannot reach port {FTP_PORT}")
            logger.error(f"  Error code: {result}")
            return False
    except Exception as e:
        logger.error(f"✗ Network connectivity test failed: {e}")
        return False


def test_sftp_connection():
    """Test SFTP connection without login"""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Testing SFTP Connection (without login)")
    logger.info("=" * 60)
    
    try:
        logger.info(f"Creating SFTP connection object to {FTP_HOST}:{FTP_PORT}")
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        
        logger.info("Attempting to connect...")
        sftp = pysftp.Connection(
            FTP_HOST,
            port=FTP_PORT,
            username=FTP_USERNAME,
            password=FTP_PASSWORD,
            cnopts=cnopts
        )
        logger.info(f"✓ SFTP connection: SUCCESS")
        logger.info(f"  Remote server: {FTP_HOST}:{FTP_PORT}")
        
        sftp.close()
        return True
    except Exception as e:
        logger.error(f"✗ SFTP connection failed: {e}")
        return False


def test_sftp_login():
    """Test SFTP connection with login"""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Testing SFTP Login")
    logger.info("=" * 60)
    
    try:
        logger.info(f"Creating SFTP connection to {FTP_HOST}:{FTP_PORT}")
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        
        logger.info(f"Connecting with username: {FTP_USERNAME}")
        sftp = pysftp.Connection(
            FTP_HOST,
            port=FTP_PORT,
            username=FTP_USERNAME,
            password=FTP_PASSWORD,
            cnopts=cnopts
        )
        logger.info(f"✓ SFTP login: SUCCESS")
        logger.info(f"  Authenticated as: {FTP_USERNAME}")
        logger.info(f"  Connected to: {FTP_HOST}:{FTP_PORT}")
        
        sftp.close()
        return True
    except Exception as e:
        logger.error(f"✗ SFTP login failed: {e}")
        return False


def test_sftp_directory():
    """Test SFTP directory access"""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: Testing SFTP Directory Access")
    logger.info("=" * 60)
    
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        
        sftp = pysftp.Connection(
            FTP_HOST,
            port=FTP_PORT,
            username=FTP_USERNAME,
            password=FTP_PASSWORD,
            cnopts=cnopts
        )
        
        logger.info(f"Attempting to access directory: {FTP_REMOTE_DIR}")
        sftp.cwd(FTP_REMOTE_DIR)
        logger.info(f"✓ Directory access: SUCCESS")
        
        logger.info(f"Listing files in {FTP_REMOTE_DIR}...")
        file_list = sftp.listdir()
        logger.info(f"✓ Found {len(file_list)} files/directories:")
        
        for item in file_list[:20]:  # Show first 20
            logger.info(f"  - {item}")
        
        if len(file_list) > 20:
            logger.info(f"  ... and {len(file_list) - 20} more")
        
        # Look for settlement report files
        settlement_files = [f for f in file_list if "auto_settle" in f.lower() and f.endswith('.xlsx')]
        if settlement_files:
            logger.info(f"\n✓ Found settlement report files:")
            for f in sorted(settlement_files):
                logger.info(f"  - {f}")
            latest = sorted(settlement_files)[-1]
            logger.info(f"\n  Latest file: {latest}")
        else:
            logger.warning(f"⚠ No settlement report files found (expected: auto_settle_*.xlsx)")
        
        sftp.close()
        return True
    except Exception as e:
        logger.error(f"✗ Directory access failed: {e}")
        return False


def main():
    logger.info("\n" + "=" * 60)
    logger.info("SFTP CONNECTIVITY DIAGNOSTIC")
    logger.info("=" * 60)
    logger.info(f"SFTP Server: {FTP_HOST}:{FTP_PORT}")
    logger.info(f"SFTP Username: {FTP_USERNAME if FTP_USERNAME else 'Anonymous'}")
    logger.info(f"SFTP Directory: {FTP_REMOTE_DIR}")
    
    # Run tests
    results = {}
    results["Network"] = test_network_connectivity()
    results["SFTP Connection"] = test_sftp_connection()
    results["SFTP Login"] = test_sftp_login()
    results["SFTP Directory"] = test_sftp_directory()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("\n✓ All tests passed! SFTP is properly configured.")
    else:
        logger.error("\n✗ Some tests failed. Check the output above for details.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
