# ten_ung_dung/core/data_manager.py

import csv
import os
from typing import List, Dict, Any, Tuple


def load_csv_data(file_path: str) -> Tuple[List[str], List[List[str]]]:
    """
    Tải dữ liệu từ tệp CSV.
    Trả về Tuple (Headers, Data). Trả về ([], []) nếu thất bại.
    """
    if not os.path.exists(file_path):
        return [], []

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)

            if not data:
                return [], []

            headers = data[0]
            rows = data[1:]
            return headers, rows

    except Exception as e:
        print(f"Lỗi khi đọc tệp {file_path}: {e}")
        return [], []


def save_csv_data(file_path: str, data_row: List[str], headers: List[str] = None):
    """
    Ghi một hàng dữ liệu mới vào tệp CSV.
    Tự động ghi header nếu tệp chưa tồn tại.
    """
    file_exists = os.path.exists(file_path)

    try:
        # Mở chế độ 'a' (append) và newline='' là chuẩn cho CSV
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            if not file_exists and headers:
                writer.writerow(headers)  # Ghi header nếu là file mới

            writer.writerow(data_row)
        return True

    except Exception as e:
        print(f"Lỗi khi ghi tệp {file_path}: {e}")
        return False