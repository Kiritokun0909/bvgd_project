import pandas as pd
import os
from datetime import datetime

from PyQt6.QtWidgets import QComboBox

from app.utils.get_file_path import get_file_path

STT_THEO_PHONG_FILE_PATH = get_file_path('data/tiep_nhan_benh_nhan/stt_theo_ngay.csv')
LICH_SU_TIEP_NHAN_FILE_PATH = get_file_path('data/lich_su_tiep_nhan.csv')


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


def load_history_records():
    if not os.path.exists(LICH_SU_TIEP_NHAN_FILE_PATH) or os.path.getsize(LICH_SU_TIEP_NHAN_FILE_PATH) == 0:
        return []
    try:
        return pd.read_csv(LICH_SU_TIEP_NHAN_FILE_PATH).to_dict('records')
    except Exception:
        return []


def can_tiep_nhan(ma_y_te: str, ma_phong: str, ngay: str) -> tuple[bool, str]:
    if not str(ma_y_te).strip():
        return True, ''

    records = [r for r in load_history_records() if
               str(r.get('MaYTe', '')).strip() == str(ma_y_te).strip() and str(r.get('NgayTiepNhan', ''))[:10] == str(
                   ngay)]
    if any(str(r.get('MaPhong', '')) == str(ma_phong) for r in records):
        return False, 'Bệnh nhân đã tiếp nhận tại phòng này trong ngày.'
    distinct_rooms = {str(r.get('MaPhong', '')) for r in records}
    if len(distinct_rooms) >= 4:
        return False, 'Bệnh nhân đã tiếp nhận tối đa 4 phòng trong ngày.'
    return True, ''


def get_next_queue_number(ma_phong: str, ngay: str = None) -> str:
    """
    Lấy và cập nhật số thứ tự tiếp theo cho một phòng dựa trên ngày hiện tại.

    :param ma_phong: Mã phòng cần lấy STT.
    :return: Chuỗi STT tiếp theo với định dạng 4 chữ số (VD: '0001').
    """
    FILE_STT = STT_THEO_PHONG_FILE_PATH

    today_str = ngay or datetime.now().strftime("%Y-%m-%d")

    # Tạo DataFrame rỗng mặc định nếu file chưa tồn tại
    if not os.path.exists(FILE_STT) or os.path.getsize(FILE_STT) == 0:
        df = pd.DataFrame(columns=['MaPhong', 'Ngay', 'STT_HienTai'])
    else:
        try:
            # Đọc dữ liệu hiện tại
            df = pd.read_csv(FILE_STT)
        except Exception as e:
            print(f"LỖI đọc file STT: {e}. Tạo DataFrame rỗng.")
            df = pd.DataFrame(columns=['MaPhong', 'Ngay', 'STT_HienTai'])

    # Đảm bảo cột STT_HienTai là số nguyên (sau khi loại bỏ '0' đứng đầu)
    if 'STT_HienTai' in df.columns:
        # Chuyển đổi về số nguyên để tính toán
        df['STT_HienTai'] = df['STT_HienTai'].astype(str).str.lstrip('0').replace('', '0').astype(int)

    # 1. Tìm bản ghi cho phòng và ngày hiện tại
    condition = (df['MaPhong'] == ma_phong) & (df['Ngay'] == today_str)

    if condition.any():
        # A. Đã tồn tại: Tăng STT lên 1
        current_index = df[condition].index[0]
        current_stt_int = df.loc[current_index, 'STT_HienTai']
        next_stt_int = current_stt_int + 1

        # Cập nhật DataFrame
        df.loc[current_index, 'STT_HienTai'] = next_stt_int
    else:
        # B. Chưa tồn tại (ngày mới hoặc phòng mới): Bắt đầu từ 1
        next_stt_int = 1
        new_row = pd.DataFrame([{'MaPhong': ma_phong, 'Ngay': today_str, 'STT_HienTai': next_stt_int}])
        df = pd.concat([df, new_row], ignore_index=True)

    # 2. Định dạng STT thành chuỗi 4 chữ số (VD: 1 -> '0001')
    next_stt_formatted = f"{next_stt_int:04d}"

    # 3. Ghi dữ liệu đã cập nhật trở lại file
    # Đảm bảo cột STT được ghi lại ở định dạng 4 chữ số
    df['STT_HienTai'] = df['STT_HienTai'].astype(int).apply(lambda x: f"{x:04d}")
    try:
        os.makedirs(os.path.dirname(str(FILE_STT)), exist_ok=True)
        df.to_csv(FILE_STT, index=False)
        print(f"STT updated for {ma_phong} on {today_str}: {next_stt_formatted}")
    except Exception as e:
        print(f"LỖI ghi file STT: {e}")

    return next_stt_formatted


def luu_du_lieu_tiep_nhan(data: dict):
    """
    Lưu toàn bộ dữ liệu tiếp nhận từ biểu mẫu vào file CSV.
    SỬA ĐỔI: Chuẩn hóa ép kiểu chuỗi độc lập cho STT, SDT, CCCD, BHYT và thêm dtype=str khi đọc file nối dữ liệu.
    """
    data = dict(data)
    data['timestamp_luu'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Chuẩn hóa STT
    stt_val = str(data.get('STT', '')).strip()
    data['STT'] = stt_val.zfill(4) if stt_val.isdigit() else stt_val

    # 2. Chuẩn hóa Số điện thoại
    if 'SDT' in data:
        data['SDT'] = str(data.get('SDT', '')).strip()

    # 3. Chuẩn hóa Căn cước công dân
    if 'CCCD' in data:
        data['CCCD'] = str(data.get('CCCD', '')).strip()

    # 4. Chuẩn hóa Số BHYT
    data['SoBHYT'] = str(data.get('SoBHYT', '')).strip().replace('.0', '')

    data['PhongTiepNhan'] = data.get('PhongTiepNhan') or data.get('Phong') or ''
    data['TenBenhVien'] = data.get('TenBenhVien') or 'BỆNH VIỆN NHÂN DÂN GIA ĐỊNH'

    # Dọn dẹp các trường dữ liệu rỗng hoặc lỗi NaN
    for key, value in list(data.items()):
        if pd.isna(value) or value is None:
            data[key] = ''
        else:
            # Ép toàn bộ value của dict về dạng chuỗi trước khi chuyển thành DataFrame
            data[key] = str(value).strip()

    df_moi = pd.DataFrame([data])

    # 3. Kiểm tra và Lưu file
    if os.path.exists(LICH_SU_TIEP_NHAN_FILE_PATH):
        # Nếu file tồn tại, đọc file cũ và nối dữ liệu mới
        try:
            df_hien_tai = pd.read_csv(LICH_SU_TIEP_NHAN_FILE_PATH)
            df_ket_hop = pd.concat([df_hien_tai, df_moi], ignore_index=True)
            df_ket_hop = df_ket_hop.fillna('')
            df_ket_hop.to_csv(LICH_SU_TIEP_NHAN_FILE_PATH, index=False, na_rep='')
            print(f"SUCCESS: Đã thêm dữ liệu mới vào {LICH_SU_TIEP_NHAN_FILE_PATH}.")
        except Exception as e:
            print(f"LỖI LƯU: Không thể đọc/ghi vào file {LICH_SU_TIEP_NHAN_FILE_PATH}. {e}")

    else:
        # Nếu file chưa tồn tại, tạo file mới
        try:
            os.makedirs(os.path.dirname(str(LICH_SU_TIEP_NHAN_FILE_PATH)), exist_ok=True)
            df_moi = df_moi.fillna('')
            df_moi.to_csv(LICH_SU_TIEP_NHAN_FILE_PATH, index=False, na_rep='')
            print(f"SUCCESS: Đã tạo và lưu dữ liệu đầu tiên vào {LICH_SU_TIEP_NHAN_FILE_PATH}.")
        except Exception as e:
            print(f"LỖI LƯU: Không thể tạo file lịch sử. {e}")