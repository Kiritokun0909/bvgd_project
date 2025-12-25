import json
import os
import csv
from datetime import datetime
from app.utils.get_file_path import get_file_path

# Định nghĩa thư mục lưu trữ gốc
TARGET_DIR = get_file_path('data/collect')


class MODE_JSON:
    PHIEU_TOA_THUOC_MODE = 0  # Toa thuốc (KhamBenhController)
    PHIEU_CHI_DINH_MODE = 1  # Chỉ định dịch vụ (DichVuController)
    HOA_DON_MODE = 2  # Hóa đơn (TaiVuController)


def generate_temp_id():
    """
    Tạo ID tạm thời giới hạn 8 ký tự cho bệnh nhân chưa có mã.
    Cấu trúc: TE + HHMMSS (Ví dụ: TE103055)
    """
    return f"TE{datetime.now().strftime('%H%M%S')}"


def get_paths(date_str, user_id):
    """
    Tạo đường dẫn thư mục và file dựa trên ngày và ID.
    Trả về: (đường dẫn json, đường dẫn csv, tên file json)
    """
    day_dir = os.path.join(TARGET_DIR, date_str)
    if not os.path.exists(day_dir):
        os.makedirs(day_dir)

    # Làm sạch user_id để tránh lỗi tên file hệ thống
    safe_id = "".join(c for c in str(user_id) if c.isalnum() or c in ('-', '_'))
    json_filename = f"{safe_id}.json"

    json_path = os.path.join(day_dir, json_filename)
    csv_path = os.path.join(day_dir, "index.csv")

    return json_path, csv_path, json_filename


def load_or_init_json(path):
    """Đọc file JSON hiện có để merge, nếu chưa có thì tạo khung rỗng."""
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass  # File lỗi hoặc trống -> tạo mới

    # Cấu trúc JSON chuẩn cho một bệnh nhân trong ngày
    return {
        "meta_data": {},
        "bills": {
            "drug_bill": None,  # Chứa dữ liệu từ Khám bệnh
            "service_bill": None,  # Chứa dữ liệu từ Dịch vụ
            "invoice": None  # Chứa dữ liệu từ Tài vụ
        }
    }


def update_index_csv(csv_path, meta_data, file_name, status_flags):
    """
    Cập nhật file index.csv đóng vai trò mục lục.
    Nếu user_id đã có -> Cập nhật dòng đó.
    Nếu chưa -> Thêm dòng mới.
    """
    fieldnames = ['datetime', 'user_id', 'user_name', 'file_name', 'has_drug', 'has_service', 'total_amount']
    rows = []
    updated = False

    # 1. Đọc dữ liệu CSV cũ (nếu có)
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except:
            rows = []

    # 2. Chuẩn bị dữ liệu dòng hiện tại
    current_row = {
        'datetime': datetime.now().strftime("%H:%M:%S"),
        'user_id': meta_data.get('user_id', ''),
        'user_name': meta_data.get('user_name', ''),
        'file_name': file_name,
        'has_drug': '1' if status_flags['has_drug'] else '0',
        'has_service': '1' if status_flags['has_service'] else '0',
        'total_amount': str(status_flags['total_amount'])
    }

    # 3. Tìm và cập nhật (hoặc thêm mới)
    for row in rows:
        if row['user_id'] == str(meta_data.get('user_id', '')):
            row.update(current_row)  # Merge thông tin mới nhất vào dòng cũ
            updated = True
            break

    if not updated:
        rows.append(current_row)

    # 4. Ghi lại file CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json_lines(new_data, mode):
    """
    Hàm chính được gọi từ Controller.
    new_data: Dictionary dữ liệu từ form.
    mode: Loại dữ liệu (Thuốc, Dịch vụ, Hóa đơn).
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    # 1. Trích xuất ID và Tên
    user_id = new_data.get('MaYTe', '')
    user_name = new_data.get('HoTen', '')

    # Xử lý trường hợp không có ID (Khách vãng lai / chưa đăng ký)
    # Nếu user_id rỗng -> Tạo mã tạm thời (8 ký tự)
    if not user_id:
        user_id = generate_temp_id()
        new_data['MaYTe'] = user_id  # Cập nhật ngược lại vào data để lưu

    # 2. Xác định đường dẫn file
    json_path, csv_path, json_filename = get_paths(date_str, user_id)

    # 3. Load dữ liệu cũ (Logic Merge)
    current_data = load_or_init_json(json_path)

    # 4. Cập nhật Meta Data (Luôn lấy thông tin mới nhất)
    current_data['meta_data'] = {
        "user_id": user_id,
        "user_name": user_name,
        "last_updated": now.strftime("%Y-%m-%d %H:%M:%S")
    }

    # 5. Lưu dữ liệu vào đúng ngăn (Slot) dựa trên Mode
    if mode == MODE_JSON.PHIEU_TOA_THUOC_MODE:
        current_data['bills']['drug_bill'] = new_data
    elif mode == MODE_JSON.PHIEU_CHI_DINH_MODE:
        current_data['bills']['service_bill'] = new_data
    elif mode == MODE_JSON.HOA_DON_MODE:
        current_data['bills']['invoice'] = new_data

    # 6. Ghi file JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=4)

    # 7. Tính toán trạng thái tổng hợp cho CSV Index
    bills = current_data['bills']

    has_drug = bool(bills.get('drug_bill'))
    has_service = bool(bills.get('service_bill'))

    # Lấy tổng tiền hiển thị ra ngoài Index (Ưu tiên: Hóa đơn -> Thuốc -> Dịch vụ)
    total_amount = "0"
    if bills.get('invoice'):
        total_amount = bills['invoice'].get('TongTienThanhToan', "0")
    elif bills.get('drug_bill'):
        total_amount = bills['drug_bill'].get('TongBenhNhanTra', "0")
    elif bills.get('service_bill'):
        total_amount = bills['service_bill'].get('TongBenhNhanTra', "0")

    status_flags = {
        'has_drug': has_drug,
        'has_service': has_service,
        'total_amount': total_amount
    }

    # 8. Cập nhật file CSV Index
    update_index_csv(csv_path, current_data['meta_data'], json_filename, status_flags)

    # print(f"[DATA SAVED] {json_filename} | Mode: {mode} | ID: {user_id}")

def get_todays_csv_rows():
    """
    Hàm chỉ đọc file index.csv và trả về danh sách các dòng (dict).
    Không đọc JSON chi tiết ở đây để đảm bảo tốc độ nhanh.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    csv_path = os.path.join(TARGET_DIR, date_str, "index.csv")

    if not os.path.exists(csv_path):
        return []

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Đảo ngược để người mới khám lên đầu
            rows.reverse()
            return rows
    except Exception as e:
        print(f"Lỗi đọc CSV: {e}")
        return []


if __name__ == '__main__':
    # Test thử tạo ID
    print(f"Test Generated ID: {generate_temp_id()}")