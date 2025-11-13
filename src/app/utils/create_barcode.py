# Cần đảm bảo có các import này ở đầu file
import os
from pathlib import Path
import barcode
from barcode.writer import ImageWriter

from app.utils.get_file_path import get_file_path

OUTPUT_DIR = get_file_path('data/hinh_anh')

BARCODE_TIEN_NAME = 'barcode_tien.png'


def generate_ma_y_te_barcode(ma_y_te: str) -> str:
    if not ma_y_te:
        return None

    # 1. Đảm bảo thư mục lưu trữ tồn tại
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Tạo tên file động và đường dẫn tuyệt đối
    safe_file_name = f"barcode_ma_y_te_{ma_y_te.replace('/', '_').replace('.', '')}"
    full_save_path = OUTPUT_DIR / safe_file_name

    # Thiết lập tùy chỉnh cho writer (luôn ẩn chữ)
    writer = ImageWriter()
    options = {
        'module_width': 0.3,
        'module_height': 15.0,
        'font_size': 0,
        'text_distance': 0.0,
        'write_text': False,  # KEY: Tắt hiển thị chuỗi số bên dưới
        'compress': False
    }

    try:
        code128 = barcode.get(
            'code128',
            ma_y_te,
            writer=writer  # Sử dụng writer đã định nghĩa cục bộ
        )

        code128.writer_options = options

        # Lưu mã vạch vào đường dẫn đầy đủ
        saved_file = code128.save(str(full_save_path), options)

        print(f"✅ Mã vạch y tế Code 128 cho '{ma_y_te}' đã được tạo thành công.")
        print(f"Tệp tin đã lưu: {saved_file}")

        # Trả về đường dẫn tuyệt đối
        return str(Path(saved_file).resolve())

    except Exception as e:
        print(f"❌ Lỗi khi tạo mã vạch y tế: {e}")
        return None


def generate_so_tien_barcode(so_tien: str, hide_text=False) -> str:

    data_to_encode = so_tien + ' VND'

    # 1. Đảm bảo thư mục lưu trữ tồn tại
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Tạo tên file động
    safe_file_name = f"barcode_tien_{so_tien.replace('.', '_').replace(',', '')}"
    full_save_path = OUTPUT_DIR / safe_file_name

    if hide_text:
        writer = ImageWriter()
        options = {
            'write_text': False,
            'module_width': 0.3,
            'module_height': 15.0,
            'font_size': 0,
        }
    else:
        # Nếu không ẩn, dùng writer mặc định và không cần options đặc biệt
        writer = ImageWriter()
        options = {}

    try:
        code128 = barcode.get(
            'code128',
            data_to_encode,
            writer=writer  # SỬA: Dùng writer đã định nghĩa trong IF/ELSE
        )

        code128.writer_options = options

        # Lưu mã vạch vào đường dẫn đầy đủ
        saved_file = code128.save(str(full_save_path), options)

        print(f"✅ Mã vạch tiền Code 128 cho '{data_to_encode}' đã được tạo thành công.")
        print(f"Tệp tin đã lưu: {saved_file}")

        return str(Path(saved_file).resolve())

    except Exception as e:
        print(f"❌ Lỗi khi tạo mã vạch: {e}")
        return None
