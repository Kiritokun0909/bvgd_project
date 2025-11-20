import sqlite3

from app.utils.constants import DB_FILE_PATH

# Giả sử bạn muốn lấy người dùng có ID = 5
# user_id = 5
# query_with_params = "SELECT name, email FROM users WHERE id = ?"
# params_tuple = (user_id,) # PHẢI là một tuple, dù chỉ có 1 phần tử

# Lấy tất cả người dùng
# query_no_params = "SELECT name, email FROM users"
# all_users = execute_query(query_no_params)

# Hoặc truyền None một cách rõ ràng (mặc dù đã có giá trị mặc định)
# all_users = execute_query(query_no_params, params=None)

# user_data = get_one_row(query_with_params, params=params_tuple)
# user_data sẽ là: ('John Doe', 'john@example.com')

def fetch_all_rows(query: str, params: tuple | None = None) -> list | None:
    conn = None
    data = None
    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()

        # print(query, params)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if query.strip().upper().startswith('SELECT'):
            data = cursor.fetchall()
        else:
            conn.commit()
            data = None

    except sqlite3.Error as e:
        print(f'❌ Lỗi SQLite: {e}')
    finally:
        if conn:
            conn.close()

    return data

def fetch_one_row(query: str, params: tuple | None = None) -> tuple | None:
    conn = None
    data = None
    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()

        # print(query)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        data = cursor.fetchone()

    except sqlite3.Error as e:
        print(f'❌ Lỗi SQLite: {e}')
    finally:
        if conn:
            conn.close()

    return data