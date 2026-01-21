import pyodbc
import sqlite3
import inspect
from tools.pull_data import db_schema
from tools.pull_data.db_schema import SQLITE_DB_PATH
from tools.pull_data.create_db_utils import create_sqlite_database
from decimal import Decimal

# --- CẤU HÌNH ---
SQL_SERVER_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'Server_name',
    'database': 'TestDB',
    'username': 'user_sql',
    'password': 'password_sql',
    'trusted_connection': 'yes'
}


def adapt_decimal(d):
    return str(d)

sqlite3.register_adapter(Decimal, adapt_decimal)


def get_sql_server_connection():
    """Tạo kết nối đến SQL Server"""
    conn_str = (
        f"DRIVER={SQL_SERVER_CONFIG['driver']};"
        f"SERVER={SQL_SERVER_CONFIG['server']};"
        f"DATABASE={SQL_SERVER_CONFIG['database']};"
        f"UID={SQL_SERVER_CONFIG['username']};"
        f"PWD={SQL_SERVER_CONFIG['password']};"
        f"Encrypt=no;"
        f"Trusted_Connection={SQL_SERVER_CONFIG['trusted_connection']};"
    )
    return pyodbc.connect(conn_str)


def generate_insert_sql(table_cls):
    col_names = [col[0] for col in table_cls.STRUCTURE]
    placeholders = ["?"] * len(col_names)

    sql = f"""
        INSERT INTO {table_cls.TABLE_NAME} ({', '.join(col_names)}) 
        VALUES ({', '.join(placeholders)})
    """
    return sql


def sync_data():
    mssql_conn = None
    sqlite_conn = None

    try:
        # 1. Mở kết nối
        print("🔌 Đang kết nối Database...")
        mssql_conn = get_sql_server_connection()
        mssql_cursor = mssql_conn.cursor()

        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_cursor = sqlite_conn.cursor()

        # Tắt check khoá ngoại tạm thời để xoá/thêm dữ liệu dễ dàng
        sqlite_cursor.execute("PRAGMA foreign_keys = OFF;")

        # 2. Duyệt qua các bảng trong Schema
        for name, cls in inspect.getmembers(db_schema, inspect.isclass):
            # Chỉ xử lý các class là bảng (có TABLE_NAME, STRUCTURE và SOURCE_QUERY)
            if hasattr(cls, 'TABLE_NAME') and hasattr(cls, 'STRUCTURE') and hasattr(cls, 'SOURCE_QUERY'):

                table_name = cls.TABLE_NAME
                source_query = cls.SOURCE_QUERY

                # Nếu không có query nguồn thì bỏ qua
                if not source_query:
                    print(f"⏭️ Bỏ qua bảng {table_name} (Không có SOURCE_QUERY)")
                    continue

                print(f"\n--------------------------------")
                print(f"📦 Đang xử lý bảng: {table_name}")

                try:
                    # A. Lấy dữ liệu từ SQL Server
                    print(f"   ⬇️  Đang fetch dữ liệu từ SQL Server...")
                    mssql_cursor.execute(source_query)
                    rows = mssql_cursor.fetchall()

                    if not rows:
                        print(f"   ⚠️ Không có dữ liệu trong SQL Server.")
                        continue

                    print(f"   ✅ Lấy được {len(rows)} dòng.")

                    # B. Xoá dữ liệu cũ trong SQLite
                    print(f"   🧹 Đang xoá dữ liệu cũ trong SQLite...")
                    sqlite_cursor.execute(f"DELETE FROM {table_name}")

                    # C. Insert dữ liệu mới
                    print(f"   ⬆️  Đang insert vào SQLite...")
                    insert_sql = generate_insert_sql(cls)
                    sqlite_cursor.executemany(insert_sql, rows)

                    print(f"   ✅ Hoàn tất bảng {table_name}!")

                except pyodbc.Error as e_sql:
                    print(f"   ❌ Lỗi SQL Server tại bảng {table_name}: {e_sql}")
                except sqlite3.Error as e_lite:
                    print(f"   ❌ Lỗi SQLite tại bảng {table_name}: {e_lite}")
                except Exception as e:
                    print(f"   ❌ Lỗi không xác định tại bảng {table_name}: {e}")

        # 3. Commit và đóng kết nối
        sqlite_conn.commit()
        print("\n--- HOÀN THÀNH ĐỒNG BỘ DỮ LIỆU ---")

    except Exception as e_main:
        print(f"❌ Lỗi hệ thống nghiêm trọng: {e_main}")

    finally:
        if mssql_conn: mssql_conn.close()
        if sqlite_conn:
            if sqlite_conn:
                # Bật lại check khoá ngoại trước khi đóng (nếu cần)
                try:
                    sqlite_conn.execute("PRAGMA foreign_keys = ON;")
                except:
                    pass
                sqlite_conn.close()


if __name__ == "__main__":
    # BƯỚC 1: Tạo cấu trúc bảng (gọi từ file utils cũ)
    print("=== BƯỚC 1: TẠO CẤU TRÚC BẢNG ===")
    create_sqlite_database()

    # BƯỚC 2: Đồng bộ dữ liệu
    print("\n=== BƯỚC 2: ĐỒNG BỘ DỮ LIỆU ===")
    sync_data()