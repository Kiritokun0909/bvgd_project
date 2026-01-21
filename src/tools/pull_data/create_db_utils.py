import sqlite3
import inspect
import db_schema
from db_schema import SQLITE_DB_PATH


def generate_create_sql(table_cls):
    columns_def = [f"{col_name} {col_type}" for col_name, col_type in table_cls.STRUCTURE]
    constraints_def = table_cls.CONSTRAINTS
    full_body_list = columns_def + constraints_def
    full_body_str = ",\n    ".join(full_body_list)
    sql = f"""
    CREATE TABLE IF NOT EXISTS {table_cls.TABLE_NAME} (
        {full_body_str}
    );
    """
    return sql


def create_sqlite_database():
    conn = None
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        print(f"✅ Đã kết nối database: {SQLITE_DB_PATH}")
        cursor = conn.cursor()

        for name, cls in inspect.getmembers(db_schema, inspect.isclass):
            if hasattr(cls, 'TABLE_NAME') and hasattr(cls, 'STRUCTURE'):
                query = generate_create_sql(cls)
                print(f"🔹 Đang tạo bảng: {cls.TABLE_NAME}...")
                cursor.execute(query)

                if hasattr(cls, 'INDEXES') and isinstance(cls.INDEXES, list):
                    for col_name in cls.INDEXES:
                        index_name = f"idx_{cls.TABLE_NAME}_{col_name}"

                        index_sql = f"""
                            CREATE INDEX IF NOT EXISTS {index_name} 
                            ON {cls.TABLE_NAME} ({col_name});
                        """
                        cursor.execute(index_sql)
                        print(f"   Build Index: {index_name} -> OK")

        conn.commit()
        print("✅ Đã tạo thành công tất cả các bảng.")

    except sqlite3.Error as e:
        print(f"❌ Lỗi kết nối SQLite: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_sqlite_database()