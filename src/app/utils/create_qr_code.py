import qrcode
from qrcode.constants import ERROR_CORRECT_M
from pathlib import Path
import os

from app.utils.get_file_path import get_file_path

# ĐỊNH NGHĨA THƯ MỤC ĐẦU RA CỤ THỂ
OUTPUT_DIR = get_file_path('data/hinh_anh')


def generate_medical_qr_code(
    ma_y_te:str,
    so_bhyt: str,
    doi_tuong: str,
    ho_ten: str,
    tuoi: str,
    gioi_tinh: str,
    dia_chi: str,
    so_dien_thoai: str,
    so_tien: str
) -> str:
    """
    Mã hóa chuỗi dữ liệu y tế và tài chính vào QR Code.
    Sử dụng định dạng chuỗi phân cách '|' để tối ưu.
    """

    # 1. Tạo chuỗi dữ liệu có cấu trúc (sử dụng '|' làm ký tự phân cách)
    data_parts = [
        f'MaYTe:{ma_y_te}',
        f"BHYT:{so_bhyt}",
        f"DTuong:{doi_tuong}",
        f"Ten:{ho_ten}",
        f"Tuoi:{tuoi}",
        f"GT:{gioi_tinh}",
        f"DC:{dia_chi}",
        f"SĐT:{so_dien_thoai}",
        f"Tien:{so_tien}"
    ]
    data_to_encode = "|".join(data_parts)

    # 2. Đảm bảo thư mục lưu trữ tồn tại
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 3. Tạo tên file động và đường dẫn tuyệt đối
    # Sử dụng BHYT và Họ Tên để đặt tên file
    safe_file_name = f"qrcode_{so_bhyt}_{ho_ten.replace(' ', '_').replace('.', '')}"
    full_save_path = OUTPUT_DIR / safe_file_name

    try:
        # Thiết lập QR Code (Mức sửa lỗi M là cân bằng tốt nhất)
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )

        # Thêm dữ liệu
        qr.add_data(data_to_encode)
        qr.make(fit=True)

        # Tạo hình ảnh
        img = qr.make_image(fill_color="black", back_color="white")

        # Lưu hình ảnh vào đường dẫn đầy đủ
        saved_file = str(full_save_path) + '.png'  # Thư viện qrcode không tự thêm đuôi
        img.save(saved_file)

        print(f"✅ Mã QR đã được tạo thành công.")
        print(f"Dữ liệu mã hóa: {data_to_encode}")
        print(f"Tệp tin đã lưu: {saved_file}")

        # Trả về đường dẫn tuyệt đối
        return str(Path(saved_file).resolve())

    except Exception as e:
        print(f"❌ Lỗi khi tạo mã QR: {e}")
        return None


if __name__ == '__main__':
    path = generate_medical_qr_code(
        ma_y_te = "DN1234567890123",
        so_bhyt="DN1234567890123",
        doi_tuong="Hộ nghèo",
        ho_ten="Trần Thị Bích",
        tuoi=45,
        gioi_tinh="Nữ",
        dia_chi="12/A Cách mạng tháng 8, Quận 3, TP.HCM",
        so_dien_thoai="0901234567",
        so_tien="350.500 VND"
    )
    print(f"\nĐường dẫn tuyệt đối của file QR: {path}")

