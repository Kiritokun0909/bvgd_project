# --- THÔNG TIN BỆNH VIỆN ---
from app.utils.get_file_path import get_file_path
from app.utils.setting_loader import AppConfig

SO_Y_TE = AppConfig.SO_Y_TE
TEN_BENH_VIEN = AppConfig.TEN_DON_VI

# --- FILE PATH ---
PHONG_KHAM_FILE_PATH = get_file_path('data/kham_benh/phong_kham.csv')
DOI_TUONG_FILE_PATH = get_file_path('data/kham_benh/doi_tuong.csv')
GIAI_QUYET_FILE_PATH = get_file_path('data/kham_benh/cach_giai_quyet.csv')
ICD_FILE_PATH = get_file_path('data/kham_benh/icd.csv')
BENH_NHAN_FILE_PATH = get_file_path('data/kham_benh/benh_nhan.csv')
THUOC_FILE_PATH = get_file_path('data/kham_benh/thuoc.csv')

# --- CẤU HÌNH TÊN CÁC CỘT TRONG FILE EXCEL BỆNH NHÂN (kham_benh/benh_nhan.csv) ---
class ExcelBenhNhan:
    COL_MA_Y_TE = 'MaYTe'
    COL_HO_TEN = 'HoTen'
    COL_MA_DOI_TUONG = 'MaDoiTuong'
    COL_GIOI_TINH = 'GioiTinh'
    COL_SO_BHYT = 'SoBHYT'
    COL_BH_TU_NGAY = 'BHTuNgay'
    COL_BH_DEN_NGAY = 'BHDenNgay'
    COL_SDT = 'SoDienThoai'
    COL_DIA_CHI = 'DiaChi'
    COL_NGAY_SINH = 'NgaySinh'

# --- CẤU HÌNH BẢNG THUỐC ---
HEADER_THUOC = [
    'Mã thuốc', 'Tên thuốc', 'Đơn vị tính',
    'Sáng', 'Trưa', 'Chiều', 'Tối',
    'Số ngày', 'Số lượng', 'Đơn giá',
    'Ghi chú', 'Huỷ']

COLUMN_REQUIRE_ONLY_NUMBER = [
    'Sáng', 'Trưa', 'Chiều', 'Tối', 'Số ngày', 'Số lượng'
]

COLUMN_REQUIRE_READ_ONLY = [
    'Mã thuốc', 'Đơn vị tính', 'Đơn giá', 'Số lượng' # Thêm Mã thuốc
]

# Mapping tên cột tiếng Việt sang tiếng Anh cho việc in/lưu trữ
FIELD_MAPPING = {
    'Mã thuốc': 'MaThuoc',
    'Tên thuốc': 'TenThuoc',
    'Đơn vị tính': 'DonViTinh',
    'Sáng': 'Sang',
    'Trưa': 'Trua',
    'Chiều': 'Chieu',
    'Tối': 'Toi',
    'Số ngày': 'SoNgay',
    'Số lượng': 'SoLuong',
    'Đơn giá': 'DonGia',
    'Ghi chú': 'GhiChu',
}

# Cập nhật Chỉ mục cột
COL_MA_THUOC = HEADER_THUOC.index('Mã thuốc')
COL_TEN_THUOC = HEADER_THUOC.index('Tên thuốc')
COL_DON_VI_TINH = HEADER_THUOC.index('Đơn vị tính')
COL_SANG = HEADER_THUOC.index('Sáng')
COL_TRUA = HEADER_THUOC.index('Trưa')
COL_CHIEU = HEADER_THUOC.index('Chiều')
COL_TOI = HEADER_THUOC.index('Tối')
COL_SO_NGAY = HEADER_THUOC.index('Số ngày')
COL_SO_LUONG = HEADER_THUOC.index('Số lượng')
COL_DON_GIA = HEADER_THUOC.index('Đơn giá')
COL_HUY = HEADER_THUOC.index('Huỷ')

DRUG_COL_COUNT = len(HEADER_THUOC)

COL_TEN_THUOC_WIDTH = 450

