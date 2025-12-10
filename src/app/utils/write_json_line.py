import json
import os

from app.utils.get_file_path import get_file_path

TARGET_DIR = get_file_path('data/collect')

TOA_THUOC_FILE_NAME = 'toa_thuoc.jsonl'
CHI_DINH_FILE_NAME = 'chi_dinh.jsonl'

class MODE_JSON:
    PHIEU_TOA_THUOC_MODE = 0
    PHIEU_CHI_DINH_MODE = 1

def write_json_lines(new_data, mode = None):
    os.makedirs(TARGET_DIR, exist_ok=True)

    filename = 'logs.jsonl'
    if mode == MODE_JSON.PHIEU_TOA_THUOC_MODE:
        filename = TOA_THUOC_FILE_NAME
    elif mode == MODE_JSON.PHIEU_CHI_DINH_MODE:
        filename = CHI_DINH_FILE_NAME

    path = os.path.join(TARGET_DIR, filename)

    # Dùng mode 'a' (append) để ghi nối tiếp vào cuối file
    with open(path, 'a', encoding='utf-8') as f:
        # Ghi dữ liệu và xuống dòng (\n)
        f.write(json.dumps(new_data, ensure_ascii=False) + '\n')
        print("Đã nối thêm dòng mới!")

if __name__ == '__main__':
    # Dữ liệu mẫu
    entry_1 = {"id": 1, "action": "login", "time": "10:00"}
    entry_2 = {"id": 1, "action": "logout", "time": "10:05"}

    os.makedirs(TARGET_DIR, exist_ok=True)

    pdf_path_1 = os.path.join(TARGET_DIR, 'logs.jsonl')

    # Chạy thử
    write_json_lines( entry_1)
    write_json_lines( entry_2)