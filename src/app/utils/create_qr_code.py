import qrcode
from qrcode.constants import ERROR_CORRECT_M, ERROR_CORRECT_Q
from pathlib import Path
import os

from app.utils.get_file_path import get_file_path
from app.utils.utils import convert_to_unsigned_preserve_case

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
    so_tien: str,
    bill_type: str = None,   # Ví dụ: "THUOC" hoặc "DICH_VU"
    items: list = None       # List dict: [{'id': 'A1', 'q': 1}, ...]
) -> str:
    """
    Mã hóa chuỗi dữ liệu y tế + danh sách thuốc/dịch vụ vào QR Code.
    Format Thuốc:   ...|Loai:THUOC|DS:ID:Qty;ID:Qty
    Format Dịch vụ: ...|Loai:DICH_VU|DS:ID:LoaiGia:Qty;ID:LoaiGia:Qty
    """

    ho_ten = convert_to_unsigned_preserve_case(ho_ten)
    gioi_tinh = convert_to_unsigned_preserve_case(gioi_tinh)
    dia_chi = convert_to_unsigned_preserve_case(dia_chi)

    # 1. Tạo chuỗi dữ liệu có cấu trúc (sử dụng '|' làm ký tự phân cách)
    data_parts = [
        f'MaYTe:{ma_y_te}',
        f"BHYT:{so_bhyt}",
        f"MaDT:{doi_tuong}",
        f"Ten:{ho_ten}",
        f"Tuoi:{tuoi}",
        f"GT:{gioi_tinh}",
        f"DC:{dia_chi}",
        f"SDT:{so_dien_thoai}",
        f"Tien:{so_tien}"
    ]

    # 2. Xử lý thêm danh sách Thuốc/Dịch vụ (Nếu có)
    if bill_type and items:
        # Thêm loại phiếu
        data_parts.append(f"Loai:{bill_type}")

        # Nén danh sách thành chuỗi: ID:Qty;ID:Qty
        # Ví dụ: 22339:1;55120:5
        item_strings = []
        for item in items:
            # Đảm bảo dữ liệu gọn nhất có thể
            id_val = str(item.get('id', '')).strip()
            qty_val = str(item.get('q', '0')).strip()

            if bill_type == 'DICH_VU':
                # Format: ID:LoaiGia:Qty:KHT:KTT
                lg_val = str(item.get('lg', '')).strip()
                kht_val = str(item.get('kht', '0')).strip()  # KhongHoTro
                ktt_val = str(item.get('ktt', '0')).strip()  # KhongThuTien

                if id_val:
                    item_strings.append(f"{id_val}:{lg_val}:{qty_val}:{kht_val}:{ktt_val}")

            else:
                # Format: ID:Qty
                if id_val:
                    item_strings.append(f"{id_val}:{qty_val}")

        if item_strings:
            compressed_list = ";".join(item_strings)
            data_parts.append(f"DS:{compressed_list}")

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
            error_correction=ERROR_CORRECT_Q,
            box_size=10,
            border=4,
        )
        qr.add_data(data_to_encode)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        saved_file = str(full_save_path) + '.png'  # Thư viện qrcode không tự thêm đuôi
        img.save(saved_file)

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
        dia_chi="12/A Cách Mạng Tháng 8, Quận 3, TP.HCM",
        so_dien_thoai="0901234567",
        so_tien="350.500 VND"
    )
    print(f"\nĐường dẫn tuyệt đối của file QR: {path}")

