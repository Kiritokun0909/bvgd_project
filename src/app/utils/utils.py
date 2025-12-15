import pandas as pd
from PyQt6 import QtCore
from PyQt6.QtWidgets import QComboBox, QCompleter
from PyQt6.QtCore import Qt
import re

from pandas.core.interchange.dataframe_protocol import DataFrame

from app.styles.styles import COMPLETER_THUOC_STYLE


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
            filtered_df = data_frame.loc[data_frame[fk_column_name].astype(str) == fk_key_value_str]

            if len(filtered_df) == 0:
                fk_key_value_str = fk_key_value_str.upper()
                filtered_df = data_frame.loc[data_frame[fk_column_name].astype(str) == fk_key_value_str]

        except KeyError:
            print(f"Lỗi lọc: Cột khóa ngoại '{fk_column_name}' không tồn tại trong dữ liệu.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Lỗi trong quá trình lọc dữ liệu: {e}")
            return pd.DataFrame()

    return filtered_df


def get_first_row_data(data_frame: pd.DataFrame) -> dict:
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

    populate_df_to_combobox(combobox, filtered_df, display_col, key_col)
    return

def populate_df_to_combobox(combobox: QComboBox, df: DataFrame, display_col: str, key_col: str):
    for index, row in df.iterrows():
        try:
            display_val = str(row[display_col])
            key_val = str(row[key_col])

            combobox.addItem(display_val)
            combobox.setItemData(combobox.count() - 1, key_val)
        except KeyError:
            print("Lỗi: Tên cột hiển thị (display_col) hoặc cột khóa (key_col) không chính xác.")
            return

def populate_list_to_combobox(combobox: QComboBox, data: list,
                              display_col: int, key_col: int):
    combobox.clear()
    length = len(data)
    for index in range(length):
        try:
            display_val = str(data[index][display_col])
            key_val = str(data[index][key_col])

            combobox.addItem(display_val)
            combobox.setItemData(combobox.count() - 1, key_val)
        except KeyError:
            print("Lỗi: Cột hiển thị (display_col) hoặc cột khóa (key_col) không chính xác.")
            return

    # 3. Bật tính năng cho phép gõ chữ (Bắt buộc cho Completer)
    combobox.setEditable(True)
    combobox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Không cho user thêm text lạ vào list

    # 4. Khởi tạo Completer sử dụng chính Model của Combobox
    # Lý do: Khi ta addItem ở bước 2, Combobox đã tự tạo một Model chứa dữ liệu đó rồi.
    completer = QCompleter()
    completer.setModel(combobox.model())

    # 5. Cấu hình thuật toán tìm kiếm
    completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Gõ "Para" hay "mol" đều ra Paracetamol
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # Không phân biệt hoa/thường

    # 6. Gán Completer vào Combobox
    completer.popup().setStyleSheet(COMPLETER_THUOC_STYLE)
    combobox.setCompleter(completer)


def get_combobox_key(combobox: QComboBox):
    """Lấy giá trị khóa (key value) của mục hiện tại."""
    return combobox.currentData()


def calculate_age(birthday):
    """Tính toán tuổi dựa trên ngày sinh."""
    date_format = "dd/MM/yyyy"

    birth_date = QtCore.QDate.fromString(str(birthday), date_format)

    if not birth_date.isValid():
        return 0

    current_date = QtCore.QDate.currentDate()
    age = current_date.year() - birth_date.year()

    if current_date.month() < birth_date.month() or \
            (current_date.month() == birth_date.month() and current_date.day() < birth_date.day()):
        age -= 1

    return age


def convert_to_unsigned_preserve_case(text):
    """
    Chuyển đổi chuỗi tiếng Việt có dấu sang không dấu,
    nhưng giữ nguyên trạng thái in hoa/thường của ký tự gốc.
    """
    if not isinstance(text, str):
        return ""

    # Ký tự Á/á, À/à, Ả/ả, ... sẽ được thay thế bằng A/a
    text = re.sub(r'[áàảãạăắằẳẵặâấầẩẫậ]', 'a', text)
    text = re.sub(r'[ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ]', 'A', text)

    text = re.sub(r'[éèẻẽẹêếềểễệ]', 'e', text)
    text = re.sub(r'[ÉÈẺẼẸÊẾỀỂỄỆ]', 'E', text)

    text = re.sub(r'[íìỉĩị]', 'i', text)
    text = re.sub(r'[ÍÌỈĨỊ]', 'I', text)

    text = re.sub(r'[óòỏõọôốồổỗộơớờởỡợ]', 'o', text)
    text = re.sub(r'[ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ]', 'O', text)

    text = re.sub(r'[úùủũụưứừửữự]', 'u', text)
    text = re.sub(r'[ÚÙỦŨỤƯỨỪỬỮỰ]', 'U', text)

    text = re.sub(r'[ýỳỷỹỵ]', 'y', text)
    text = re.sub(r'[ÝỲỶỸỴ]', 'Y', text)

    # Chữ Đ/đ
    text = re.sub(r'đ', 'd', text)
    text = re.sub(r'Đ', 'D', text)

    return text.strip()


def format_currency_vn(amount, decimal_places=3):
    """
    Định dạng số tiền theo chuẩn Việt Nam: 1.786.000,000

    :param amount: Số (int hoặc float) cần định dạng.
    :param decimal_places: Số chữ số thập phân muốn hiển thị sau dấu phẩy.
    :return: Chuỗi đã định dạng.
    """
    # Làm tròn và định dạng số
    # Dùng '{:,.Xf}' để định dạng với dấu phẩy là phân cách hàng nghìn, và dấu chấm là thập phân
    amount = float(amount)
    format_spec = f",.{decimal_places}f"

    # B1: Định dạng số mặc định (ví dụ: '1,786,000.000')
    amount_str_default = f"{amount:{format_spec}}"

    # B2: Tách phần nguyên và phần thập phân
    parts = amount_str_default.split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else '0' * decimal_places

    # B3: Xử lý phần nguyên: Thay dấu phẩy phân cách hàng nghìn bằng dấu chấm
    formatted_integer = integer_part.replace(',', '.')

    # B4: Kết hợp lại: Dùng dấu phẩy làm phân cách thập phân
    return f"{formatted_integer},{decimal_part}"


def unformat_currency_to_float(formatted_string):
    """
    Chuyển đổi chuỗi định dạng tiền tệ VN (1.786.000,000) thành float (1786000.0)

    :param formatted_string: Chuỗi giá tiền cần chuyển đổi.
    :return: Số float tương ứng.
    """
    if not isinstance(formatted_string, str):
        # Nếu đầu vào không phải chuỗi, thử ép kiểu hoặc trả về ngay nếu đã là số
        if isinstance(formatted_string, (int, float)):
            return float(formatted_string)
        return float(str(formatted_string))

    # Bước 1: Loại bỏ dấu phân cách hàng nghìn (dấu chấm '.')
    # Ví dụ: '1.786.000,000' -> '1786000,000'
    temp_string = formatted_string.replace('.', '')

    # Bước 2: Thay thế dấu phân cách thập phân (dấu phẩy ',') bằng dấu chấm '.'
    # Ví dụ: '1786000,000' -> '1786000.000'
    final_string = temp_string.replace(',', '.')

    # Bước 3: Chuyển đổi chuỗi kết quả thành float
    try:
        return float(final_string)
    except ValueError:
        print(f"Lỗi: Không thể chuyển đổi '{formatted_string}' thành số.")
        return None