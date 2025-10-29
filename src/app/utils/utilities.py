import pandas as pd
from PyQt6.QtWidgets import QComboBox

from app.core.tiep_nhan_benh_nhan import load_data_from_csv, populate_combobox

def _setup_combobox_from_csv(self, field_name, file_path, display_col, key_col, default_key=None):
    """
    :param field_name: Tên của trường (key) trong self.data_widgets.
    :param file_path: Đường dẫn đến file CSV.
    :param display_col: Tên cột hiển thị.
    :param key_col: Tên cột giá trị khóa (key value).
    :param default_key: (TÙY CHỌN) Giá trị khóa (key value) để đặt làm mặc định.
    """
    # 1. Tải dữ liệu
    data_frame = load_data_from_csv(file_path)

    # 2. Lấy widget tương ứng
    combobox = self.data_widgets.get(field_name)

    if combobox is None:
        print(f"LỖI: Không tìm thấy widget cho trường '{field_name}'.")
        return

    if not data_frame.empty:
        # 3. Điền dữ liệu vào ComboBox
        populate_combobox(combobox, data_frame, display_col, key_col)

        # 4. >>> LOGIC THIẾT LẬP GIÁ TRỊ MẶC ĐỊNH DỰA TRÊN KEY <<<
        if default_key is not None:
            index = combobox.findData(str(default_key))
            if index >= 0:
                combobox.setCurrentIndex(index)
                return  # Thoát khỏi hàm nếu đã tìm thấy và đặt mặc định

        # Nếu không có key mặc định hoặc không tìm thấy key: chọn mục đầu tiên
        combobox.setCurrentIndex(0)

    else:
        print(f"CẢNH BÁO: Dữ liệu CSV cho '{field_name}' rỗng hoặc bị lỗi.")
