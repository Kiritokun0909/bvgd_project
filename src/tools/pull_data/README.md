# Pull Data Tool

Tool hỗ trợ đồng bộ dữ liệu từ SQL Server về SQLite database cục bộ (`data/hospital.db`). Tool được thiết kế để tự động hoá việc tạo bảng và migrant dữ liệu dựa trên cấu hình code.

## 📂 Các file chính

1. **`db_schema.py`**: Nơi định nghĩa cấu trúc bảng (Schema) và câu truy vấn lấy dữ liệu (Source Query).
2. **`create_db_utils.py`**: Chứa hàm `generate_create_sql` và logic loop qua schema để tạo văn bản `CREATE TABLE` và `INDEX`.
3. **`main_etl.py`**: Script chính thực thi luồng ETL (Extract - Transform - Load): Kết nối SQL Server -> Kết nối SQLite -> Tạo bảng -> Xoá data cũ -> Insert data mới.

---

## 🚀 Hướng dẫn sử dụng

### 1. Cài đặt thư viện
Tool yêu cầu thư viện `pyodbc` để kết nối với SQL Server khi chạy script `main_etl.py`. Mở terminal và chạy lệnh sau để cài đặt:
```bash
pip install pyodbc
```

### 2. Cấu hình kết nối
Kiểm tra cấu hình SQL Server trong file `main_etl.py`:
```
SQL_SERVER_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'Server_name',
    ...
}
```

### 3. Chạy đồng bộ
Mở terminal và chạy lệnh:
```bash
python -m src.tools.pull_data.main_etl
# Hoặc chạy trực tiếp nếu đang đứng ở root project đúng
```

---

## ⚠️ LƯU Ý ĐẶC BIỆT QUAN TRỌNG (HÃY ĐỌC KỸ)

### 1. Quy tắc về thứ tự Field (STRUCTURE vs SOURCE_QUERY)

Trong file `db_schema.py`, mỗi Class đại diện cho một bảng. Bạn cần định nghĩa `STRUCTURE` (cấu trúc bảng đích) và `SOURCE_QUERY` (câu lệnh lấy dữ liệu nguồn).

> **Lưu ý:**
> **Thứ tự các trường (field) trong `STRUCTURE` PHẢI KHỚP TUYỆT ĐỐI với thứ tự các cột được SELECT trong `SOURCE_QUERY`.**

Tool sẽ map dữ liệu theo thứ tự vị trí (index-based), không map theo tên cột. Nếu thứ tự bị lệch, dữ liệu sẽ bị insert sai cột hoặc gây lỗi kiểu dữ liệu.

**Ví dụ ĐÚNG ✅:**
```python
# 1. STRUCTURE khai báo ID trước, Tên sau
STRUCTURE = [
    ('BenhNhan_Id', 'INTEGER'),  # Vị trí 1
    ('TenBenhNhan', 'TEXT')      # Vị trí 2
]

# 2. SOURCE_QUERY cũng phải SELECT ID trước, Tên sau
SOURCE_QUERY = """
    SELECT 
        BenhNhan_Id,   -- Vị trí 1 (Khớp)
        TenBenhNhan    -- Vị trí 2 (Khớp)
    FROM DM_BenhNhan
"""
```

**Ví dụ SAI ❌:**
```python
STRUCTURE = [('Id', '...'), ('Name', '...')]

# SELECT Name trước Id -> Dữ liệu Name sẽ bị nhét vào cột Id -> LỖI
SOURCE_QUERY = "SELECT Name, Id FROM ..." 
```

### 2. Quy tắc khi thay đổi cấu trúc bảng (Schema Change)

Cơ chế tạo bảng của tool là `CREATE TABLE IF NOT EXISTS`. Nghĩa là nếu file database đã có bảng đó rồi, nó sẽ **KHÔNG** tạo lại, cũng **KHÔNG** tự động alter column.

> **Nếu bạn sửa đổi `STRUCTURE` (thêm cột, xoá cột, sửa tên cột, đổi data type) trong code:**
> 1. Bạn **BẮT BUỘC PHẢI XOÁ** file database cũ (`data/hospital.db`).
> 2. Chạy lại tool để nó tạo lại file `.db` mới với cấu trúc bảng mới nhất.

Nếu bạn quên xoá file `.db` cũ, code Python mới sẽ cố insert dữ liệu vào bảng SQLite cũ -> Gây lỗi `OperationalError: table has x columns but y values were supplied` hoặc sai lệch dữ liệu.
