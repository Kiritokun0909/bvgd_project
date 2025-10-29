import pandas as pd
from PyQt6.QtWidgets import QComboBox

def load_data_from_csv(file_path):
    """
    Đọc dữ liệu từ file CSV.
    LƯU Ý: Hàm này chỉ đọc một file (không phải nhiều sheet như Excel).
    """
    try:
        # Giả sử file CSV sử dụng dấu phẩy (,) làm delimiter và có header
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"LỖI: Không thể đọc file CSV '{file_path}'. {e}")
        return pd.DataFrame()  # Trả về DataFrame rỗng nếu có lỗi


def filter_data_by_foreign_key(data_frame: pd.DataFrame,
                               fk_key_value=None,
                               fk_column_name=None) -> pd.DataFrame:
    """
    Lọc DataFrame dựa trên giá trị khóa ngoại.

    :param data_frame: DataFrame nguồn cần lọc.
    :param fk_key_value: Giá trị khóa ngoại dùng để lọc (có thể là None).
    :param fk_column_name: Tên cột chứa khóa ngoại (có thể là None).
    :return: DataFrame đã được lọc, hoặc DataFrame gốc nếu không có điều kiện lọc.
    """
    filtered_df = data_frame

    # Chỉ thực hiện lọc nếu cả hai tham số khóa ngoại đều được cung cấp
    if fk_key_value is not None and fk_column_name is not None:
        try:
            # Chuyển giá trị khóa ngoại sang chuỗi để so sánh nhất quán
            fk_key_value_str = str(fk_key_value)

            # Lọc DataFrame: so sánh cột khóa ngoại (cũng được chuyển sang chuỗi)
            # với giá trị khóa ngoại cung cấp.
            filtered_df = data_frame.loc[data_frame[fk_column_name].astype(str) == fk_key_value_str]

        except KeyError:
            print(f"Lỗi lọc: Cột khóa ngoại '{fk_column_name}' không tồn tại trong dữ liệu.")
            return pd.DataFrame()  # Trả về DataFrame rỗng nếu lỗi
        except Exception as e:
            print(f"Lỗi trong quá trình lọc dữ liệu: {e}")
            return pd.DataFrame()

    return filtered_df


def get_first_row_data(data_frame: pd.DataFrame) -> dict | None:
    """
    Trả về dữ liệu của dòng đầu tiên trong DataFrame dưới dạng dictionary.
    Trả về None nếu DataFrame rỗng.
    """
    if data_frame.empty:
        return None

    # Sử dụng iloc[0].to_dict() để lấy dữ liệu của dòng đầu tiên
    return data_frame.iloc[0].to_dict()

def populate_combobox(combobox: QComboBox, display_col: str, key_col: str, file_path: str,
                      fk_key_value=None, fk_column_name=None):
    """
    Đổ dữ liệu vào QComboBox từ DataFrame được tải từ CSV.
    display_col và key_col phải là tên cột (header) trong CSV.

    Tham số tùy chọn:
    :param file_path:
    :param key_col:
    :param display_col:
    :param combobox:
    :param fk_key_value: Giá trị khóa ngoại dùng để lọc.
    :param fk_column_name: Tên cột chứa khóa ngoại.

    Chỉ thực hiện lọc nếu cả fk_key_value và fk_column_name đều khác None.
    """
    combobox.clear()

    # Giả sử hàm load_data_from_csv được định nghĩa và có thể tải dữ liệu
    try:
        data_frame = load_data_from_csv(file_path)
    except NameError:
        print("Lỗi: Vui lòng định nghĩa hàm 'load_data_from_csv' để tải dữ liệu.")
        return
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu từ CSV: {e}")
        return

    # --- BẮT ĐẦU LOGIC LỌC ---
    filtered_df = data_frame

    # 2. Lọc dữ liệu bằng hàm mới
    filtered_df = filter_data_by_foreign_key(
        data_frame,
        fk_key_value=fk_key_value,
        fk_column_name=fk_column_name
    )

    # Đổ dữ liệu đã lọc vào QComboBox
    for index, row in filtered_df.iterrows():
        try:
            display_value = str(row[display_col])
            key_value = str(row[key_col])

            combobox.addItem(display_value)
            # Lưu giá trị khóa (key value) vào item data
            combobox.setItemData(combobox.count() - 1, key_value)
        except KeyError:
            print("Lỗi: Tên cột hiển thị (display_col) hoặc cột khóa (key_col) không chính xác.")
            return


def get_combobox_key(combobox: QComboBox):
    """Lấy giá trị khóa (key value) của mục hiện tại."""
    return combobox.currentData()