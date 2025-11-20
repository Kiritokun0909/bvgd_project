class Schema:
    """
    Lớp hằng số chứa tên các bảng và các cột (thuộc tính) trong database.
    Mỗi lớp con đại diện cho một bảng.
    """

    class BenhNhan:
        TABLE_NAME = 'BenhNhan'
        SO_VAO_VIEN = 'SoVaoVien'
        TEN_BENH_NHAN = 'TenBenhNhan'
        GIOI_TINH = 'GioiTinh'
        NAM_SINH = 'NamSinh'
        SO_DIEN_THOAI = 'SoDienThoai'
        DIA_CHI = 'DiaChi'

    class DoiTuong:
        TABLE_NAME = 'DoiTuong'
        DOI_TUONG_ID = 'DoiTuong_Id'
        MA_DOI_TUONG = 'MaDoiTuong'
        TEN_DOI_TUONG = 'TenDoiTuong'
        GIOI_HAN_1 = 'GioiHan_1'
        TY_LE_1 = 'TyLe_1'
        TY_LE_2 = 'TyLe_2'

    class ICD:
        TABLE_NAME = 'ICD'
        MA_ICD = 'MaICD'
        TEN_ICD = 'TenICD'

    class DM_Duoc:
        TABLE_NAME = 'DM_Duoc'
        DUOC_ID = 'Duoc_Id'
        MA_DUOC = 'MaDuoc'
        TEN_DUOC_DAY_DU = 'TenDuocDayDu'
        DON_GIA = 'DonGia'
        TEN_DON_VI_TINH = 'TenDonViTinh'
        DICTIONARY_NAME = 'Dictionary_Name'

    class PhongBan:
        TABLE_NAME = 'PhongBan'
        PHONG_BAN_ID = 'PhongBan_Id'
        MA_PHONG_BAN = 'MaPhongBan'
        TEN_PHONG_BAN = 'TenPhongBan'

    class NhomDichVu:
        TABLE_NAME = 'NhomDichVu'
        NHOM_DICH_VU_ID = 'NhomDichVu_Id'
        TEN_NHOM_DICH_VU = 'TenNhomDichVu'

    class DMDichVu:
        TABLE_NAME = 'DichVu'
        DICH_VU_ID = 'DichVu_Id'
        INPUT_CODE = 'InputCode'
        NHOM_DICH_VU_ID = 'NhomDichVu_Id'
        TEN_DICH_VU = 'TenDichVu'
        TEN_KHONG_DAU = 'TenKhongDau'

    class LoaiGia:
        TABLE_NAME = 'LoaiGia'
        LOAI_GIA_ID = 'LoaiGia_Id'
        MA_LOAI_GIA = 'MaLoaiGia'
        TEN_LOAI_GIA = 'TenLoaiGia'

    class GiaDichVu:
        TABLE_NAME = 'GiaDichVu'
        DICH_VU_ID = 'DichVu_Id'
        LOAI_GIA_ID = 'LoaiGia_Id'
        DON_GIA = 'DonGia'

    class PhongBanDichVu:
        TABLE_NAME = 'PhongBanDichVu'
        DICH_VU_ID = 'DichVu_Id'
        PHONG_BAN_ID = 'PhongBan_Id'
        PHONG_BAN_DICH_VU_ID = 'PhongBan_DichVu_Id'

    class DoiTuongLoaiGia:
        TABLE_NAME = 'DoiTuongLoaiGia'
        DOI_TUONG_ID = 'DoiTuong_Id'
        LOAI_GIA_ID = 'LoaiGia_Id'
        DOI_TUONG_LOAI_GIA_ID = 'DoiTuong_LoaiGia_Id'
        DO_UU_TIEN = 'DoUuTien'