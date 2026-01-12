import configparser
from pathlib import Path
import sys
import os

def get_config_path(filename='settings.ini'):
    # 1. Nếu đang chạy từ PyInstaller (--onefile)
    if getattr(sys, 'frozen', False):
        # sys.executable: /path/to/dist/main/main.exe
        # Path(sys.executable).parent: /path/to/dist/main/
        # .parent: /path/to/dist/  <-- Đây là thư mục chứa settings.ini và data/

        # Đảm bảo lấy được đường dẫn tuyệt đối của thư mục dist/
        DIST_DIR = Path(sys.executable).resolve().parent.parent

        return DIST_DIR / filename
    # 2. Nếu đang chạy code Python bình thường (trong PyCharm)
    else:
        # Sử dụng logic cũ: tìm thư mục 'src' từ vị trí file hiện tại
        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        return PROJECT_ROOT / filename


CONFIG_FILE = get_config_path()

class AppConfig:
    SO_Y_TE = 'Chưa xác định'
    TEN_DON_VI = "Chưa xác định"
    MA_SO_THUE = "Chưa xác định"
    DIA_CHI = "Chưa xác định"
    SDT = "Chưa xác định"
    LOGO_FILE_NAME = 'logo.png'
    DB_FILE_NAME = 'hospital.db'
    CLS_CODE = 'GQ06'
    USERNAME_THONG_TUYEN_BHYT = 'Username'
    PASSWORD_THONG_TUYEN_BHYT = 'Password'
    HO_TEN_CAN_BO = 'Nguyen Van A'
    CCCD_CAN_BO = '012345678936'


def load_config():
    # 1. Khởi tạo ConfigParser
    parser = configparser.ConfigParser()

    # 2. Kiểm tra file
    if not os.path.exists(CONFIG_FILE):
        print(f"Lỗi: Không tìm thấy file cấu hình '{CONFIG_FILE}'. Sử dụng giá trị mặc định.")
        print(f"Đang tìm kiếm tại: {os.path.abspath(CONFIG_FILE)}")
        return

    # 3. Đọc file
    parser.read(CONFIG_FILE, encoding='utf-8')

    # 4. Gán các giá trị từ file vào class AppConfig
    AppConfig.SO_Y_TE = parser.get('THONG_TIN_CHUNG', 'SO_Y_TE', fallback=AppConfig.SO_Y_TE)
    AppConfig.TEN_DON_VI = parser.get('THONG_TIN_CHUNG', 'TEN_DON_VI', fallback=AppConfig.TEN_DON_VI)
    AppConfig.MA_SO_THUE = parser.get('THONG_TIN_CHUNG', 'MA_SO_THUE', fallback=AppConfig.MA_SO_THUE)
    AppConfig.DIA_CHI = parser.get('THONG_TIN_CHUNG', 'DIA_CHI', fallback=AppConfig.DIA_CHI)
    AppConfig.SDT = parser.get('THONG_TIN_CHUNG', 'SDT', fallback=AppConfig.SDT)
    AppConfig.LOGO_FILE_NAME = parser.get('THONG_TIN_CHUNG', 'LOGO_FILE_NAME', fallback=AppConfig.LOGO_FILE_NAME)
    AppConfig.DB_FILE_NAME = parser.get('THONG_TIN_CHUNG', 'DB_FILE_NAME', fallback=AppConfig.DB_FILE_NAME)
    AppConfig.CLS_CODE = parser.get('THONG_TIN_CHUNG', 'CLS_CODE', fallback=AppConfig.CLS_CODE)
    AppConfig.USERNAME_THONG_TUYEN_BHYT = parser.get('THONG_TIN_CHUNG', 'USERNAME_THONG_TUYEN_BHYT',
                                                     fallback=AppConfig.USERNAME_THONG_TUYEN_BHYT)
    AppConfig.PASSWORD_THONG_TUYEN_BHYT = parser.get('THONG_TIN_CHUNG', 'PASSWORD_THONG_TUYEN_BHYT',
                                                     fallback=AppConfig.PASSWORD_THONG_TUYEN_BHYT)
    AppConfig.HO_TEN_CAN_BO = parser.get('THONG_TIN_CHUNG', 'HO_TEN_CAN_BO', fallback=AppConfig.HO_TEN_CAN_BO)
    AppConfig.CCCD_CAN_BO = parser.get('THONG_TIN_CHUNG', 'CCCD_CAN_BO', fallback=AppConfig.CCCD_CAN_BO)


# Thực hiện tải cấu hình ngay khi module này được import
load_config()