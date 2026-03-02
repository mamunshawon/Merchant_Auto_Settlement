# Auto Settlement with SFTP Integration

## Feature Overview

This project now includes automated SFTP file fetching capability. The workflow is:

1. **Fetch from SFTP Server**: Automatically retrieves the latest `auto_settle_failure_report_YYYYMMDD.xlsx` file from the SFTP server
2. **Process Minutes**: Adjusts the MINUTE column according to the business logic
3. **Auto Settlement Update**: Updates merchant auto-settlement configurations with the new hours and minutes

## SFTP Configuration

### Protocol: SFTP (SSH File Transfer Protocol)
The project uses **SFTP on port 40167** (OpenSSH), not traditional FTP.

### Required SFTP Settings

The following environment variables must be configured in your `.env` file:

- `FTP_HOST`: SFTP server IP (default: 10.210.10.201)
- `FTP_PORT`: SFTP server port (default: 40167)
- `FTP_USERNAME`: SFTP login username
- `FTP_PASSWORD`: SFTP login password
- `FTP_REMOTE_DIR`: Remote directory path (default: /home/techops/auto_settlement_report)

### Setup Instructions

1. Ensure the project dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
   This includes `pysftp` and `paramiko` for SFTP support.

2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your SFTP credentials:
   ```env
   FTP_HOST=10.210.10.201
   FTP_PORT=40167
   FTP_USERNAME=your_sftp_username
   FTP_PASSWORD=your_sftp_password
   FTP_REMOTE_DIR=/home/techops/auto_settlement_report
   ```

## Testing SFTP Connection

Before running the main script, test your SFTP configuration:

```bash
python test_ftp_connectivity.py
```

This will perform comprehensive diagnostics:
1. **Network Connectivity**: Verify port 40167 is reachable
2. **SFTP Connection**: Test SSH connection
3. **SFTP Login**: Authenticate with provided credentials
4. **Directory Access**: Access remote directory and list files

**Sample Output (Success)**:
```
STEP 1: Testing Network Connectivity
✓ Network connectivity: SUCCESS - Port 40167 is reachable

STEP 2: Testing SFTP Connection (without login)
✓ SFTP connection: SUCCESS

STEP 3: Testing SFTP Login
✓ SFTP login: SUCCESS
  Authenticated as: techops

STEP 4: Testing SFTP Directory Access
✓ Directory access: SUCCESS
✓ Found settlement report files:
  - auto_settle_failure_report_20260301.xlsx
  - auto_settle_failure_report_20260302.xlsx
```

## Minute Adjustment Logic

The minute column is automatically adjusted using the following logic:

| Original Minute | New Minute | Hour Offset |
|-----------------|-----------|------------|
| 0               | 15        | 0          |
| 15              | 30        | 0          |
| 30              | 45        | 0          |
| 45              | 0         | +1         |

**Example**:
- If a merchant has `HOUR=10, MINUTE=45`, it will be adjusted to `HOUR=11, MINUTE=0`
- Hour values wrap around (23:45 → 0:00 next cycle)

## Excel File Format

The SFTP file must contain the following columns:
- `MERCHANT_ID`: Unique merchant identifier
- `HOUR`: Hour value (0-23)
- `MINUTE`: Minute value (0, 15, 30, or 45 recommended)

### Sample File

```
MERCHANT_ID,HOUR,MINUTE
MERCH001,09,00
MERCH002,14,30
MERCH003,23,45
```

## File Processing Workflow

1. **Automatic SFTP Fetch**: When the script runs, it automatically:
   - Connects to SFTP server via SSH
   - Authenticates with provided credentials
   - Lists available files in the remote directory
   - Finds and downloads the latest settlement report file
   - Saves it as `input.xlsx` locally

2. **Data Processing**: The downloaded file is then:
   - Read using pandas
   - Validated for required columns
   - Minutes are adjusted according to the business logic
   - Processed merchants are extracted

3. **Auto Settlement**: Finally:
   - Each merchant's configuration is fetched from the system
   - Updated with new hour and minute values
   - Results are logged and reported

## Modules

### `services/ftp_client.py`
Handles SFTP server connection and file downloading using PySSH.

**Key Classes**:
- `FTPClient`: Manages SFTP connections and file transfers

**Key Methods**:
- `connect()`: Establish SFTP connection using SSH
- `disconnect()`: Close SFTP connection
- `fetch_file()`: Download specific file via SFTP
- `fetch_latest_settlement_report()`: Download latest settlement report file

### `services/data_processor.py`
Processes merchant data and adjusts minutes.

**Key Classes**:
- `DataProcessor`: Handles data transformation and minute adjustment

**Key Methods**:
- `adjust_minute()`: Adjust minute value by 15-minute increments
- `process_merchant_data()`: Process entire DataFrame of merchants

## Dependencies

- Python 3.7+
- pandas (for Excel file reading)
- python-dotenv (for environment configuration)
- selenium (for browser automation)
- openpyxl (for Excel file support)
- **paramiko** (for SSH protocol support)
- **pysftp** (for SFTP file transfer)

All dependencies are listed in `requirements.txt`.

## Error Handling

The system includes comprehensive error handling:

- **SFTP Connection Errors**: Logged with full details for investigation
- **Authentication Failures**: Checks credentials and SSH access
- **Missing File**: Raises exception if no settlement report files found
- **Invalid Data**: Validates required columns before processing
- **Hour Wraparound**: Handles 24-hour cycle automatically

## Logging

All operations are logged to help with debugging:

- `SFTP_CLIENT`: SFTP connection and file transfer logs
- `DATA_PROCESSOR`: Data processing and transformation logs
- `MAIN`: Overall workflow and status logs

## Running the Script

```bash
# Install dependencies first
pip install -r requirements.txt

# Test SFTP connectivity
python test_ftp_connectivity.py

# Run the main script
python main.py
```

The script will:
1. Fetch the latest file from SFTP
2. Process merchant data with minute adjustments
3. Update all merchant configurations
4. Generate a report of changes

## Troubleshooting

### SFTP Connection Issues
- Verify `FTP_HOST=10.210.10.201`, `FTP_PORT=40167`
- Check `FTP_USERNAME` and `FTP_PASSWORD` are correct for SFTP server
- Ensure SSH access is enabled on the SFTP server
- Check firewall allows connection to 10.210.10.201:40167

### File Not Found
- Verify `FTP_REMOTE_DIR=/home/techops/auto_settlement_report` exists
- Check that files match pattern: `auto_settle_failure_report_*.xlsx`
- Ensure files are uploaded to SFTP before running script
- Run diagnostic to verify directory access: `python test_ftp_connectivity.py`

### Data Processing Issues
- Verify Excel file contains MERCHANT_ID, HOUR, MINUTE columns
- Check that MINUTE values are 0, 15, 30, or 45
- Review logs for specific error messages

### SSH/SFTP Authentication
- Confirm credentials work with standard SFTP client:
  ```bash
  sftp -P 40167 username@10.210.10.201
  ```
- Verify SSH public key authentication (if configured)
- Check server logs for connection attempts

## Migration from FTP to SFTP

If you were previously using standard FTP, this change migrates to SFTP (SSH File Transfer Protocol) which provides:
- **Security**: Encrypted file transfer via SSH
- **Better Performance**: Optimized protocol for modern systems
- **Compatibility**: Works with OpenSSH servers

No code changes are required - the `FTPClient` class abstraction handles both protocols transparently.
