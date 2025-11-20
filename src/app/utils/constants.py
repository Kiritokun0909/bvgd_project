from app.utils.get_file_path import get_file_path
from app.utils.setting_loader import AppConfig

MA_Y_TE_LENGTH = 8

# --- THÔNG TIN BỆNH VIỆN ---
SO_Y_TE = AppConfig.SO_Y_TE
TEN_BENH_VIEN = AppConfig.TEN_DON_VI

CLS_CODE = f'{AppConfig.CLS_CODE}'
DB_FILE_PATH = get_file_path(f'data/{AppConfig.DB_FILE_NAME}')

GIAI_QUYET_FILE_PATH = get_file_path('data/cach_giai_quyet.csv')