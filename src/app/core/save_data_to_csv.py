import pandas as pd
import os
from datetime import datetime

def luu_du_lieu_tiep_nhan(data: dict):
    """
    Lưu toàn bộ dữ liệu tiếp nhận từ biểu mẫu vào file CSV.
    """
    LICH_SU_TIEP_NHAN_FILE_PATH = "data/lich_su_tiep_nhan.csv"

    # 1. Thêm timestamp để theo dõi thời điểm lưu
    data['timestamp_luu'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Chuyển đổi dictionary thành DataFrame
    df_moi = pd.DataFrame([data])

    # 3. Kiểm tra và Lưu file
    if os.path.exists(LICH_SU_TIEP_NHAN_FILE_PATH):
        # Nếu file tồn tại, đọc file cũ và nối dữ liệu mới
        try:
            df_hien_tai = pd.read_csv(LICH_SU_TIEP_NHAN_FILE_PATH)
            df_ket_hop = pd.concat([df_hien_tai, df_moi], ignore_index=True)
            df_ket_hop.to_csv(LICH_SU_TIEP_NHAN_FILE_PATH, index=False)
            print(f"SUCCESS: Đã thêm dữ liệu mới vào {LICH_SU_TIEP_NHAN_FILE_PATH}.")
        except Exception as e:
            print(f"LỖI LƯU: Không thể đọc/ghi vào file {LICH_SU_TIEP_NHAN_FILE_PATH}. {e}")

    else:
        # Nếu file chưa tồn tại, tạo file mới
        try:
            os.makedirs(os.path.dirname(LICH_SU_TIEP_NHAN_FILE_PATH), exist_ok=True)
            df_moi.to_csv(LICH_SU_TIEP_NHAN_FILE_PATH, index=False)
            print(f"SUCCESS: Đã tạo và lưu dữ liệu đầu tiên vào {LICH_SU_TIEP_NHAN_FILE_PATH}.")
        except Exception as e:
            print(f"LỖI LƯU: Không thể tạo file lịch sử. {e}")