# --- HẰNG SỐ FILE PATH ---
PHONG_KHAM_FILE_PATH = 'data/kham_benh/phong_kham.csv'
DANH_MUC_FILE_PATH = 'data/dich_vu/danh_muc_dich_vu.csv'
DICH_VU_FILE_PATH = 'data/dich_vu/dich_vu.csv'
DOI_TUONG_FILE_PATH = 'data/kham_benh/doi_tuong.csv'

# Giả định các cột cần thiết trong DICH_VU_FILE_PATH
SERVICE_CODE_COLUMN = 'MaDichVu'
DICH_VU_ID_COLUMN = 'MaDichVu'

SERVICE_NAME_COLUMN = 'TenDichVu'
DICH_VU_NAME_COLUMN = 'TenDichVu'

SERVICE_CAT_COLUMN = 'MaDanhMuc'
SERVICE_PRICE_COLUMN = 'DonGia'
SERVICE_TEN_KHONG_DAU_COLUMN = 'TenDichVuKhongDau'

# --- CẤU HÌNH BẢNG DỊCH VỤ ---
HEADER_DICH_VU = [
    'Mã dịch vụ', 'Mã nhóm dịch vụ', 'Tên dịch vụ', 'Số lượng','Đơn giá doanh thu',
    'Tỷ lệ TT', 'Thành tiền doanh thu', 'Loại giá', 'Bảo hiểm thanh toán',
    'Bệnh nhân thanh toán', 'Không thu tiền', 'Không hỗ trợ', 'Chọn in',
    'Nơi thực hiện', 'Số phiếu', 'Lý do không thu', 'Huỷ']

# Các cột cần kiểm tra chỉ được nhập số
COLUMN_REQUIRE_ONLY_NUMBER = [
    'Tỷ lệ TT',
    # 'Số lượng' (cột này không có trong HEADER_DICH_VU, nhưng thường là số)
]

# Các cột được tự động điền hoặc tính toán, không cho phép chỉnh sửa thủ công
COLUMN_REQUIRE_READ_ONLY = [
    'Mã dịch vụ',
    'Mã nhóm dịch vụ',
    'Đơn giá doanh thu',
    'Thành tiền doanh thu',
    'Bảo hiểm thanh toán',
    'Bệnh nhân thanh toán',
]

# Mapping tên cột tiếng Việt sang tiếng Anh cho việc in/lưu trữ
FIELD_MAPPING = {
    'Mã dịch vụ': 'MaDichVu',
    'Tên dịch vụ': 'TenDichVu',
    'Đơn giá doanh thu': 'DonGiaDoanhThu',
    'Tỷ lệ TT': 'TyLeTT',
    'Thành tiền doanh thu': 'ThanhTienDoanhThu',
    'Loại giá': 'LoaiGia',
    'Bảo hiểm thanh toán': 'BHThanhToan',
    'Bệnh nhân thanh toán': 'BNThanhToan',
    'Không thu tiền': 'KhongThuTien',
    'Không hỗ trợ': 'KhongHoTro',
    'Chọn in': 'ChonIn',
    'Nơi thực hiện': 'NoiThucHien',
    'Số phiếu': 'SoPhieu',
    'Lý do không thu': 'LyDoKhongThu',
}

# Cập nhật Chỉ mục cột
COL_MA_DV = HEADER_DICH_VU.index('Mã dịch vụ')
COL_MA_NHOM_DV = HEADER_DICH_VU.index('Mã nhóm dịch vụ')
COL_TEN_DV = HEADER_DICH_VU.index('Tên dịch vụ')
COL_SO_LUONG = HEADER_DICH_VU.index('Số lượng')
COL_DON_GIA_DOANH_THU = HEADER_DICH_VU.index('Đơn giá doanh thu')
COL_TY_LE_TT = HEADER_DICH_VU.index('Tỷ lệ TT')
COL_THANH_TIEN_DOANH_THU = HEADER_DICH_VU.index('Thành tiền doanh thu')
COL_LOAI_GIA = HEADER_DICH_VU.index('Loại giá')
COL_BH_TT = HEADER_DICH_VU.index('Bảo hiểm thanh toán')
COL_BN_TT = HEADER_DICH_VU.index('Bệnh nhân thanh toán')
COL_KHONG_THU_TIEN = HEADER_DICH_VU.index('Không thu tiền')
COL_KHONG_HO_TRO = HEADER_DICH_VU.index('Không hỗ trợ')
COL_CHON_IN = HEADER_DICH_VU.index('Chọn in')
COL_NOI_THUC_HIEN = HEADER_DICH_VU.index('Nơi thực hiện')
COL_SO_PHIEU = HEADER_DICH_VU.index('Số phiếu')
COL_LY_DO_KHONG_THU = HEADER_DICH_VU.index('Lý do không thu')
COL_HUY = HEADER_DICH_VU.index('Huỷ')

DICH_VU_COL_COUNT = len(HEADER_DICH_VU)

COL_SERVICE_TABLE_DEFAULT_WIDTH = 150

ADD_FROM_SEARCHBOX = 0
ADD_FROM_TREE_ITEM = 1

SERVICE_SEARCH_COLUMN = 'TenDichVuTimKiem'

TREE_COL_DICH_VU_CHECKBOX = 0
TREE_COL_DICH_VU = 1

SEARCHING_AFTER_NUM_OF_CHAR = 1
SEARCH_TIMEOUT = 200