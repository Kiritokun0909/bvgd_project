# --- CẤU HÌNH CÁC TIÊU ĐỀ CỘT BẢNG THUỐC ---
HEADER_THUOC = [
    'Mã thuốc', 'Tên thuốc', 'Đơn vị tính',
    'Sáng', 'Trưa', 'Chiều', 'Tối',
    'Số ngày', 'Số lượng', 'Đơn giá', 'Đường dùng',
    'Ghi chú', 'Huỷ']

COLUMN_REQUIRE_ONLY_NUMBER = [
    'Sáng', 'Trưa', 'Chiều', 'Tối', 'Số ngày', 'Số lượng'
]

COLUMN_REQUIRE_READ_ONLY = [
    'Mã thuốc', 'Đơn vị tính', 'Đơn giá', 'Số lượng', 'Đường dùng'
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
    'Đường dùng': 'DuongDung',
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
COL_DUONG_DUNG = HEADER_THUOC.index('Đường dùng')
COL_HUY = HEADER_THUOC.index('Huỷ')

DRUG_COL_COUNT = len(HEADER_THUOC)

COL_TEN_THUOC_WIDTH = 450

