# --- THÔNG TIN BỆNH VIỆN ---
TEN_BENH_VIEN = "BỆNH VIỆN ABC"
SO_Y_TE = "SỞ Y TẾ XYZ"

PHIEU_TOA_THUOC_HEADER = 'ĐƠN THUỐC BHYT'

# --- FILE PATH ---
PHONG_KHAM_FILE_PATH = 'data/kham_benh/phong_kham.csv'
DOI_TUONG_FILE_PATH = 'data/kham_benh/doi_tuong.csv'
GIAI_QUYET_FILE_PATH = 'data/kham_benh/cach_giai_quyet.csv'
ICD_FILE_PATH = 'data/kham_benh/icd.csv'
BENH_NHAN_FILE_PATH = 'data/kham_benh/benh_nhan.csv'
THUOC_FILE_PATH = 'data/kham_benh/thuoc.csv'

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

