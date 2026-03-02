# Auto Settlement with FTP Integration

## Feature Overview

This project now includes automated FTP file fetching capability. The workflow is:

1. **Fetch from FTP Server**: Automatically retrieves the latest `auto_settle_failure_report_YYYYMMDD.xlsx` file from the FTP server
2. **Process Minutes**: Adjusts the MINUTE column according to the business logic
3. **Auto Settlement Update**: Updates merchant auto-settlement configurations with the new hours and minutes

## FTP Configuration

### Required FTP Settings

The following environment variables must be configured in your `.env` file:

- `FTP_HOST`: FTP server IP (default: 10.210.10.201)
- `FTP_PORT`: FTP server port (default: 40167)
- `FTP_USERNAME`: FTP login username (optional, for anonymous access)
- `FTP_PASSWORD`: FTP login password (optional, for anonymous access)
- `FTP_REMOTE_DIR`: Remote directory path (default: /home/techops/auto_settlement_report)

### Setup Instructions

1. Copy `.env.example` to `.env`:
   ```
   cp .env.example .env
   ```

2. Update `.env` with your FTP credentials:
   ```
   FTP_HOST=10.210.10.201
   FTP_PORT=40167
   FTP_USERNAME=your_username
   FTP_PASSWORD=your_password
   FTP_REMOTE_DIR=/home/techops/auto_settlement_report
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

The FTP file must contain the following columns:
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

1. **Automatic FTP Fetch**: When the script runs, it automatically:
   - Connects to the FTP server
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
Handles FTP server connection and file downloading.

**Key Classes**:
- `FTPClient`: Manages FTP connections and file transfers

**Key Methods**:
- `connect()`: Establish connection to FTP server
- `disconnect()`: Close FTP connection
- `fetch_file()`: Download specific file
- `fetch_latest_settlement_report()`: Download latest settlement report file

### `services/data_processor.py`
Processes merchant data and adjusts minutes.

**Key Classes**:
- `DataProcessor`: Handles data transformation and minute adjustment

**Key Methods**:
- `adjust_minute()`: Adjust minute value by 15-minute increments
- `process_merchant_data()`: Process entire DataFrame of merchants

## Error Handling

The system includes comprehensive error handling:

- **FTP Connection Errors**: Logged and raised for investigation
- **Missing File**: Raises exception if no settlement report files found
- **Invalid Data**: Validates required columns before processing
- **Hour Wraparound**: Handles 24-hour cycle automatically

## Logging

All operations are logged to help with debugging:

- `FTP_CLIENT`: FTP connection and file transfer logs
- `DATA_PROCESSOR`: Data processing and transformation logs
- `MAIN`: Overall workflow and status logs

## Running the Script

```bash
python main.py
```

The script will:
1. Fetch the latest file from FTP
2. Process merchant data with minute adjustments
3. Update all merchant configurations
4. Generate a report of changes

## Troubleshooting

### FTP Connection Issues
- Verify FTP_HOST, FTP_PORT, FTP_USERNAME, and FTP_PASSWORD in `.env`
- Check firewall rules allow connection to 10.210.10.201:40167
- Ensure FTP credentials are correct

### File Not Found
- Verify FTP_REMOTE_DIR path exists on FTP server
- Check that file matches pattern: `auto_settle_failure_report_*.xlsx`
- Ensure files are uploaded to FTP before running script

### Data Processing Issues
- Verify Excel file contains MERCHANT_ID, HOUR, MINUTE columns
- Check that MINUTE values are 0, 15, 30, or 45
- Review logs for specific error messages

## Dependencies

- Python 3.7+
- pandas (for Excel file reading)
- python-dotenv (for environment configuration)
- selenium (for browser automation)
- openpyxl (for Excel file support)

All dependencies are listed in `requirements.txt`.
