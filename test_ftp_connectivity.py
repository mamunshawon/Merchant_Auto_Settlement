#!/usr/bin/env python3
"""
FTP Connectivity Diagnostic Script
Tests FTP connection with detailed debugging output
"""

import socket
from ftplib import FTP
from config.settings import FTP_HOST, FTP_PORT, FTP_USERNAME, FTP_PASSWORD, FTP_REMOTE_DIR
from utils.logger import get_logger

logger = get_logger("FTP_DIAGNOSTIC")


def test_network_connectivity():
    """Test basic network connectivity to FTP server"""
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


def test_ftp_connection():
    """Test FTP connection without login"""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: Testing FTP Connection (without login)")
    logger.info("=" * 60)
    
    try:
        logger.info(f"Creating FTP connection object to {FTP_HOST}:{FTP_PORT}")
        ftp = FTP()
        ftp.set_debuglevel(2)
        
        logger.info("Attempting to connect...")
        ftp.connect(FTP_HOST, FTP_PORT, timeout=60)
        logger.info(f"✓ FTP connection: SUCCESS")
        logger.info(f"  Server welcome message: {ftp.welcome}")
        
        ftp.quit()
        return True
    except Exception as e:
        logger.error(f"✗ FTP connection failed: {e}")
        return False


def test_ftp_login():
    """Test FTP connection with login"""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: Testing FTP Login")
    logger.info("=" * 60)
    
    try:
        logger.info(f"Creating FTP connection to {FTP_HOST}:{FTP_PORT}")
        ftp = FTP()
        ftp.set_debuglevel(2)
        
        logger.info(f"Connecting with timeout 60 seconds...")
        ftp.connect(FTP_HOST, FTP_PORT, timeout=60)
        logger.info(f"✓ Connection established")
        logger.info(f"  Welcome: {ftp.welcome}")
        
        if FTP_USERNAME and FTP_PASSWORD:
            logger.info(f"Attempting login as: {FTP_USERNAME}")
            response = ftp.login(FTP_USERNAME, FTP_PASSWORD)
            logger.info(f"✓ FTP login: SUCCESS")
            logger.info(f"  Login response: {response}")
        else:
            logger.info("No credentials provided, attempting anonymous login...")
            response = ftp.login()
            logger.info(f"✓ Anonymous login: SUCCESS")
            logger.info(f"  Login response: {response}")
        
        ftp.quit()
        return True
    except Exception as e:
        logger.error(f"✗ FTP login failed: {e}")
        return False


def test_ftp_directory():
    """Test FTP directory access"""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: Testing FTP Directory Access")
    logger.info("=" * 60)
    
    try:
        ftp = FTP()
        ftp.set_debuglevel(2)
        ftp.connect(FTP_HOST, FTP_PORT, timeout=60)
        
        if FTP_USERNAME and FTP_PASSWORD:
            ftp.login(FTP_USERNAME, FTP_PASSWORD)
        else:
            ftp.login()
        
        logger.info(f"Attempting to change to directory: {FTP_REMOTE_DIR}")
        ftp.cwd(FTP_REMOTE_DIR)
        logger.info(f"✓ Directory access: SUCCESS")
        
        logger.info(f"Listing files in {FTP_REMOTE_DIR}...")
        file_list = ftp.nlst()
        logger.info(f"✓ Found {len(file_list)} files/directories:")
        for item in file_list[:10]:  # Show first 10
            logger.info(f"  - {item}")
        
        if len(file_list) > 10:
            logger.info(f"  ... and {len(file_list) - 10} more")
        
        # Look for settlement report files
        settlement_files = [f for f in file_list if "auto_settle" in f.lower()]
        if settlement_files:
            logger.info(f"\n✓ Found settlement report files:")
            for f in settlement_files:
                logger.info(f"  - {f}")
        else:
            logger.warning(f"⚠ No settlement report files found (expected: auto_settle_*.xlsx)")
        
        ftp.quit()
        return True
    except Exception as e:
        logger.error(f"✗ Directory access failed: {e}")
        return False


def main():
    logger.info("\n" + "=" * 60)
    logger.info("FTP CONNECTIVITY DIAGNOSTIC")
    logger.info("=" * 60)
    logger.info(f"FTP Server: {FTP_HOST}:{FTP_PORT}")
    logger.info(f"FTP Username: {FTP_USERNAME if FTP_USERNAME else 'Anonymous'}")
    logger.info(f"FTP Directory: {FTP_REMOTE_DIR}")
    
    # Run tests
    results = {}
    results["Network"] = test_network_connectivity()
    results["FTP Connection"] = test_ftp_connection()
    results["FTP Login"] = test_ftp_login()
    results["FTP Directory"] = test_ftp_directory()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("\n✓ All tests passed! FTP is properly configured.")
    else:
        logger.error("\n✗ Some tests failed. Check the output above for details.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
