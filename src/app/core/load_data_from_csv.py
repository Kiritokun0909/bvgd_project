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


def populate_combobox(combobox: QComboBox, data_frame: pd.DataFrame, display_col, key_col):
    """
    Điền dữ liệu vào QComboBox từ DataFrame.
    display_col và key_col phải là tên cột (header) trong CSV.
    """
    combobox.clear()
    for index, row in data_frame.iterrows():
        # Đảm bảo chuyển đổi sang chuỗi
        display_value = str(row[display_col])
        key_value = str(row[key_col])

        # Thêm giá trị hiển thị và lưu giá trị khóa (key value)
        combobox.addItem(display_value)
        combobox.setItemData(combobox.count() - 1, key_value)


def get_combobox_key(combobox: QComboBox):
    """Lấy giá trị khóa (key value) của mục hiện tại."""
    return combobox.currentData()