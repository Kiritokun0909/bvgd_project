# BVGD Project

## Overview
BVGD Project is a desktop application designed for hospital management tasks, including Patient Registration (*Khám Bệnh*), Service Registration (*Đăng ký Dịch vụ*), and Cashier/Finance (*Tài Vụ*).

The application operates with a local SQLite database for offline capability/speed, which is synchronized from a central SQL Server database using a built-in ETL tool.

## Tech Stack
- **Language**: Python 3.8+
- **GUI Framework**: PyQt6
- **Database**:
    - **Remote**: SQL Server (Microsoft SQL Server)
    - **Local**: SQLite
- **Libraries**:
    - `pyodbc`: For SQL Server connectivity.
    - `sqlite3`: Native Python library for local database.
- **Packaging**: PyInstaller (for executable generation).

## Project Structure
- `src/`: Source code directory.
    - `app/`: Main application logic (Controllers, UI, Services).
    - `tools/`: Utility scripts, primarily for data synchronization.
        - `main_etl.py`: ETL script to sync data from SQL Server to SQLite.
        - `db_schema.py`: Definition of database tables and schemas.
    - `main.py`: Entry point for the GUI application.
- `requirements.txt`: Python project dependencies.
- `main.spec`: PyInstaller specification file for building the executable.

## Setup & Installation

### 1. Prerequisites
- Python 3.8 or higher.
- ODBC Driver 17 for SQL Server.
- Recommend using **Pycharm, QtDesigner** to maintain this project.

### 2. Install Dependencies
It is recommended to use a virtual environment.

```bash
# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configuration
**Database Connection:**
The ETL tool currently uses configuration settings defined in `src/tools/main_etl.py`.
Open `src/tools/main_etl.py` and submit your SQL Server credentials in the `SQL_SERVER_CONFIG` dictionary:

```python
SQL_SERVER_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'YOUR_SERVER_NAME',
    'database': 'YOUR_DATABASE_NAME',
    'username': 'YOUR_USERNAME',
    'password': 'YOUR_PASSWORD',
    'trusted_connection': 'no' # Set to 'yes' if using Windows Authentication
}
```

**Application Settings:**
The application also uses a `settings.ini` file for general hospital information and UI configuration. This file should be located in the same directory as the executable (or `src/` during development).

Create a `settings.ini` file with the following structure:

```ini
[THONG_TIN_CHUNG]
SO_Y_TE = Sở Y Tế Tỉnh X
TEN_DON_VI = Bệnh Viện Đa Khoa Y
MA_SO_THUE = 123456789
DIA_CHI = 123 Đường ABC, Phường XYZ
SDT = 024.1234.5678
LOGO_FILE_NAME = logo.png
DB_FILE_NAME = hospital.db
CLS_CODE = GQ06 # Notice this code must be the same with CLS in cach_giai_quyet.csv
USERNAME_THONG_TUYEN_BHYT = username # username for login BHXH VN
PASSWORD_THONG_TUYEN_BHYT = password # password
HO_TEN_CAN_BO = Nguyen Van A # Tên cán bộ được cấp quyền tìm kiếm
CCCD_CAN_BO = 012345678936  # Số CCCD của cán bộ được cấp quyền trên cổng PIS
```

## How to Run

### 1. Initialize & Sync Data (ETL)
Before running the application, you need to prepare the local database.

```bash
python src/tools/main_etl.py
```
This script will:
1.  Create the SQLite database structure (`data/hospital.db`).
2.  Fetch data from the configured SQL Server.
3.  Populate the local SQLite database.

### 2. Run the Application
Start the main desktop interface:

```
python src/main.py
```

## Building Executable
To build a standalone executable using the provided spec file:
```
pyinstaller --windowed .\src\main.py
```
The output file will be located in the `dist/` directory.


# Other Tools
 * To extract correctly data from your own database to **hospital.db**, you need
to open **src/tools/README.md** and follow instruction.

 * To copy and sync program to multiple machines in local network and schedule
to run it weekly, please read **src/tools/sync_app/README.md** and follow
instruction.
   