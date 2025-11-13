from pathlib import Path
import sys
import os

def get_file_path(file_path):
    # 1. Nếu đang chạy từ PyInstaller (--onefile)
    if getattr(sys, 'frozen', False):
        # sys.executable: /path/to/dist/main/main.exe
        # Path(sys.executable).parent: /path/to/dist/main/
        # .parent: /path/to/dist/  <-- Đây là thư mục chứa settings.ini và data/

        # Đảm bảo lấy được đường dẫn tuyệt đối của thư mục dist/
        DIST_DIR = Path(sys.executable).resolve().parent.parent

        return DIST_DIR / file_path
    # 2. Nếu đang chạy code Python bình thường (trong PyCharm)
    else:
        # Sử dụng logic cũ: tìm thư mục 'src' từ vị trí file hiện tại
        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        return PROJECT_ROOT / file_path