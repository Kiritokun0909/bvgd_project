import pandas as pd
import os
from datetime import datetime

def get_next_queue_number(ma_phong: str) -> str:
    """
    Lấy và cập nhật số thứ tự tiếp theo cho một phòng dựa trên ngày hiện tại.

    :param ma_phong: Mã phòng cần lấy STT.
    :return: Chuỗi STT tiếp theo với định dạng 4 chữ số (VD: '0001').
    """
    FILE_STT = "data/tiep_nhan_benh_nhan/stt_theo_ngay.csv"

    # Định dạng ngày hiện tại để so sánh
    today_str = datetime.now().strftime("%Y-%m-%d")

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
        os.makedirs(os.path.dirname(FILE_STT), exist_ok=True)
        df.to_csv(FILE_STT, index=False)
        print(f"STT updated for {ma_phong} on {today_str}: {next_stt_formatted}")
    except Exception as e:
        print(f"LỖI ghi file STT: {e}")

    return next_stt_formatted