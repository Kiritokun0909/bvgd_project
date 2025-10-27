import pandas as pd
import os
from datetime import datetime

def luu_du_lieu_tiep_nhan(data: dict):
    """
    Lưu toàn bộ dữ liệu tiếp nhận từ biểu mẫu vào file CSV.
    """
    FILE_LICH_SU = "data/lich_su_tiep_nhan.csv"

    # 1. Thêm timestamp để theo dõi thời điểm lưu
    data['timestamp_luu'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Chuyển đổi dictionary thành DataFrame
    df_moi = pd.DataFrame([data])

    # 3. Kiểm tra và Lưu file
    if os.path.exists(FILE_LICH_SU):
        # Nếu file tồn tại, đọc file cũ và nối dữ liệu mới
        try:
            df_hien_tai = pd.read_csv(FILE_LICH_SU)
            df_ket_hop = pd.concat([df_hien_tai, df_moi], ignore_index=True)
            df_ket_hop.to_csv(FILE_LICH_SU, index=False)
            print(f"SUCCESS: Đã thêm dữ liệu mới vào {FILE_LICH_SU}.")
        except Exception as e:
            print(f"LỖI LƯU: Không thể đọc/ghi vào file lịch sử. {e}")

    else:
        # Nếu file chưa tồn tại, tạo file mới
        try:
            os.makedirs(os.path.dirname(FILE_LICH_SU), exist_ok=True)
            df_moi.to_csv(FILE_LICH_SU, index=False)
            print(f"SUCCESS: Đã tạo và lưu dữ liệu đầu tiên vào {FILE_LICH_SU}.")
        except Exception as e:
            print(f"LỖI LƯU: Không thể tạo file lịch sử. {e}")