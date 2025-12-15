
# Giả định các cột cần thiết trong DICH_VU_FILE_PATH
SERVICE_CODE_COLUMN = 'MaDichVu'
DICH_VU_ID_COLUMN = 'MaDichVu'

SERVICE_NAME_COLUMN = 'TenDichVu'
DICH_VU_NAME_COLUMN = 'TenDichVu'

SERVICE_CAT_COLUMN = 'MaDanhMuc'
SERVICE_PRICE_COLUMN = 'DonGia'
SERVICE_TEN_KHONG_DAU_COLUMN = 'TenKhongDau'

# --- CẤU HÌNH BẢNG DỊCH VỤ ---
HEADER_DICH_VU = [
    'DichVuId', 'Mã dịch vụ', 'Mã nhóm dịch vụ', 'Tên dịch vụ', 'Số lượng','Đơn giá doanh thu',
    'Tỷ lệ TT', 'Thành tiền doanh thu', 'Mã loại giá', 'Loại giá', 'Bảo hiểm thanh toán',
    'Bệnh nhân thanh toán', 'Không thu tiền', 'Không hỗ trợ', 'Chọn in',
    'Nơi thực hiện', 'Số phiếu', 'Lý do không thu', 'Huỷ']

# Các cột cần kiểm tra chỉ được nhập số
COLUMN_REQUIRE_ONLY_NUMBER = [
    'Tỷ lệ TT',
    # 'Số lượng' (cột này không có trong HEADER_DICH_VU, nhưng thường là số)
]

# Các cột được tự động điền hoặc tính toán, không cho phép chỉnh sửa thủ công
COLUMN_REQUIRE_READ_ONLY = [
    'DichVuId',
    'Mã dịch vụ',
    'Mã nhóm dịch vụ',
    'Đơn giá doanh thu',
    'Thành tiền doanh thu',
    'Bảo hiểm thanh toán',
    'Bệnh nhân thanh toán',
]

# Cập nhật Chỉ mục cột
COL_DICH_VU_ID = HEADER_DICH_VU.index('DichVuId')
COL_MA_DV = HEADER_DICH_VU.index('Mã dịch vụ')
COL_MA_NHOM_DV = HEADER_DICH_VU.index('Mã nhóm dịch vụ')
COL_TEN_DV = HEADER_DICH_VU.index('Tên dịch vụ')
COL_SO_LUONG = HEADER_DICH_VU.index('Số lượng')
COL_DON_GIA_DOANH_THU = HEADER_DICH_VU.index('Đơn giá doanh thu')
COL_TY_LE_TT = HEADER_DICH_VU.index('Tỷ lệ TT')
COL_THANH_TIEN_DOANH_THU = HEADER_DICH_VU.index('Thành tiền doanh thu')
COL_MA_LOAI_GIA = HEADER_DICH_VU.index('Mã loại giá')
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

COL_MA_DANH_MUC_HEADER = 'MaDanhMuc'
COL_TEN_DANH_MUC_HEADER = 'TenDanhMuc'

class DANH_MUC:
    COL_MA_DANH_MUC_HEADER = 'MaDanhMuc'
    COL_TEN_DANH_MUC_HEADER = 'TenDanhMuc'

class LOAI_GIA:
    COL_MA_LOAI_GIA_HEADER = 'MaLoaiGia'
    COL_TEN_LOAI_GIA_HEADER = 'TenLoaiGia'

class DOI_TUONG_LOAI_GIA:
    COL_MA_DOI_TUONG_HEADER = 'MaDoiTuong'
    COL_MA_LOAI_GIA_HEADER = 'MaLoaiGia'
    ThuTuUuTien = 'ThuTuUuTien'

class DON_GIA:
    COL_MA_DICH_VU_HEADER = 'MaDichVu'
    COL_MA_LOAI_GIA_HEADER = 'MaLoaiGia'
    COL_DON_GIA_HEADER = 'DonGia'

FIELD_MAPPING = {
    'DichVuId': 'DichVuId',
    'Mã dịch vụ': 'MaDichVu',
    'Mã nhóm dịch vụ': 'MaNhomDichVu',
    'Tên dịch vụ': 'TenDichVu',
    'Số lượng': 'SoLuong',
    'Đơn giá doanh thu': 'DonGiaDoanhThu',
    'Tỷ lệ TT': 'TyLeTT',
    'Thành tiền doanh thu': 'TTDoanhThu',
    'Mã loại giá': 'MaLoaiGia',
    'Loại giá': 'LoaiGia',
    'Bảo hiểm thanh toán': 'BaoHiemTT',
    'Bệnh nhân thanh toán': 'BenhNhanTT',
    'Không thu tiền': 'KhongThuTien',
    'Không hỗ trợ': 'KhongHoTro',
    'Chọn in': 'ChonIn',
    'Nơi thực hiện': 'NoiThucHien',
    'Số phiếu': 'SoPhieu',
    'Lý do không thu': 'LyDoKhongThu',
}

MIN_COLUMN_WIDTH = 80
MIN_COLUMN_HEIGHT = 50

SEARCH_BY_INPUT_CODE = 0
SEARCH_BY_DICH_VU_ID = 1