# Dự án BVGD (BVGD Project)

## Tổng quan
Dự án BVGD là một ứng dụng máy tính dành cho các công việc quản lý bệnh viện, bao gồm Khám Bệnh (Patient Registration), Đăng ký Dịch vụ (Service Registration), và Tài Vụ (Cashier/Finance).

Ứng dụng hoạt động với cơ sở dữ liệu SQLite cục bộ để có khả năng ngoại tuyến/tốc độ cao, được đồng bộ hóa từ cơ sở dữ liệu SQL Server trung tâm bằng công cụ ETL tích hợp.

## Công nghệ sử dụng
- **Ngôn ngữ**: Python 3.8+
- **Framework giao diện**: PyQt6
- **Cơ sở dữ liệu**:
    - **Máy chủ (Remote)**: SQL Server (Microsoft SQL Server)
    - **Cục bộ (Local)**: SQLite
- **Thư viện**:
    - `pyodbc`: Để kết nối SQL Server.
    - `sqlite3`: Thư viện Python mặc định cho cơ sở dữ liệu cục bộ.
- **Đóng gói**: PyInstaller (để tạo tệp thực thi).

## Cấu trúc dự án
- `src/`: Thư mục mã nguồn.
    - `app/`: Logic ứng dụng chính (Controllers, UI, Services).
    - `tools/`: Các mã nguồn tiện ích, chủ yếu dùng để đồng bộ hóa dữ liệu.
        - `main_etl.py`: Mã nguồn ETL để đồng bộ dữ liệu từ SQL Server sang SQLite.
        - `db_schema.py`: Định nghĩa các bảng và sơ đồ cơ sở dữ liệu.
    - `main.py`: Điểm khởi đầu của ứng dụng giao diện (GUI).
- `requirements.txt`: Các thư viện phụ thuộc của dự án.
- `main.spec`: Tệp cấu hình PyInstaller để đóng gói ứng dụng.

## Cấu hình & Cài đặt

### 1. Điều kiện tiên quyết
- Python 3.8 trở lên.
- ODBC Driver 17 cho SQL Server.
- Khuyến nghị sử dụng **Pycharm, QtDesigner** để bảo trì dự án này.

### 2. Cài đặt các thư viện phụ thuộc
Khuyên dùng môi trường ảo (virtual environment).

```bash
# Tạo môi trường ảo (tùy chọn nhưng khuyên dùng)
python -m venv .venv
source .venv/bin/activate  # Trên Windows: .venv\Scripts\activate

# Cài đặt các thư viện
pip install -r requirements.txt
```

### 3. Cấu hình
**Kết nối cơ sở dữ liệu:**
Công cụ ETL hiện đang sử dụng các thiết lập cấu hình được định nghĩa trong `src/tools/main_etl.py`.
Mở `src/tools/main_etl.py` và điền thông tin đăng nhập SQL Server của bạn vào biến `SQL_SERVER_CONFIG`:

```python
SQL_SERVER_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'YOUR_SERVER_NAME',
    'database': 'YOUR_DATABASE_NAME',
    'username': 'YOUR_USERNAME',
    'password': 'YOUR_PASSWORD',
    'trusted_connection': 'no' # Đặt thành 'yes' nếu sử dụng Windows Authentication
}
```

**Cài đặt ứng dụng:**
Ứng dụng cũng sử dụng tệp `settings.ini` cho các thông tin bệnh viện chung và cấu hình giao diện. Tệp này nên được đặt trong cùng thư mục với tệp thực thi (hoặc trong thư mục `src/` khi đang phát triển).

Tạo tệp `settings.ini` với cấu trúc như sau:

```ini
[THONG_TIN_CHUNG]
SO_Y_TE = Sở Y Tế Tỉnh X
TEN_DON_VI = Bệnh Viện Đa Khoa Y
MA_SO_THUE = 123456789
DIA_CHI = 123 Đường ABC, Phường XYZ
SDT = 024.1234.5678
LOGO_FILE_NAME = logo.png
DB_FILE_NAME = hospital.db
CLS_CODE = GQ06 # Lưu ý mã này phải giống với mã CLS trong cach_giai_quyet.csv
USERNAME_THONG_TUYEN_BHYT = username # tên đăng nhập cổng BHXH VN
PASSWORD_THONG_TUYEN_BHYT = password # mật khẩu
HO_TEN_CAN_BO = Nguyen Van A # Tên cán bộ được cấp quyền tìm kiếm
CCCD_CAN_BO = 012345678936  # Số CCCD của cán bộ được cấp quyền trên cổng PIS
```

## Cách khởi chạy

### 1. Khởi tạo & Đồng bộ dữ liệu (ETL)
Trước khi khởi chạy ứng dụng, bạn cần chuẩn bị cơ sở dữ liệu cục bộ.

```
python src/tools/main_etl.py
```
Tiện ích này sẽ:
1.  Tạo cấu trúc cơ sở dữ liệu SQLite (`data/hospital.db`).
2.  Lấy dữ liệu từ SQL Server đã cấu hình.
3.  Lưu dữ liệu vào cơ sở dữ liệu SQLite cục bộ.

### 2. Chạy ứng dụng
Khởi động giao diện chính của ứng dụng:

```
python src/main.py
```

## Đóng gói tệp thực thi (Build Executable)
Để tạo tệp thực thi độc lập bằng tệp spec có sẵn:
```
pyinstaller --onefile --windowed --name="PhanMemBenhVien" .\src\main.py
```
Tệp kết quả sẽ nằm trong thư mục `dist/`.


# Các công cụ khác
 * Để trích xuất dữ liệu chính xác từ cơ sở dữ liệu của riêng bạn sang **hospital.db**, vui lòng đọc 
**src/tools/README.md** và làm theo hướng dẫn.

 * Để sao chép và đồng bộ chương trình cho nhiều máy trong mạng nội bộ và lên lịch
chạy hàng tuần, vui lòng đọc **src/tools/sync_app/README.md** và làm theo
hướng dẫn.