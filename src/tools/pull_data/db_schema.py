SQLITE_DB_PATH = 'data/hospital.db'

"""
    Nơi định nghĩa cấu trúc Database.
    Mỗi Inner Class là một bảng.
    - STRUCTURE: List các tuple (Tên cột, Kiểu dữ liệu)
    - CONSTRAINTS: List các ràng buộc bảng (Primary key phức hợp, Foreign key...)
    - SOURCE_QUERY: Query lấy data từ db gốc
"""


class BenhNhan:
    TABLE_NAME = 'BenhNhan'
    BENH_NHAN_ID = 'BenhNhan_Id'
    SO_VAO_VIEN = 'SoVaoVien'
    TEN_BENH_NHAN = 'TenBenhNhan'
    GIOI_TINH = 'GioiTinh'
    NAM_SINH = 'NamSinh'
    SO_DIEN_THOAI = 'SoDienThoai'
    DIA_CHI = 'DiaChi'
    BHYT = 'BHYT'

    # Định nghĩa cấu trúc (Tên cột, Kiểu dữ liệu SQLite)
    STRUCTURE = [
        (BENH_NHAN_ID, "INTEGER PRIMARY KEY"),
        (SO_VAO_VIEN, "TEXT"),
        (TEN_BENH_NHAN, "TEXT"),
        (GIOI_TINH, "TEXT"),
        (NAM_SINH, "INTEGER"),
        (SO_DIEN_THOAI, "TEXT"),
        (DIA_CHI, "TEXT"),
        (BHYT, "TEXT")
    ]
    CONSTRAINTS = []

    INDEXES = [SO_VAO_VIEN]

    # Query lấy dữ liệu từ SQL Server (Số lượng cột và thứ tự phải khớp với STRUCTURE)
    SOURCE_QUERY = f"""
        SELECT  bn.BenhNhan_Id, SoVaoVien, TenBenhNhan, GioiTinh, NamSinh, SoDienThoai, DiaChi, the.SoThe as BHYT
        FROM DM_BenhNhan bn
        OUTER apply (
            SELECT top 1 * FROM DM_BenhNhan_BHYT a WHERE a.benhnhan_id=bn.BenhNhan_Id 
            ORDER BY benhnhan_bhyt_id DESC) the
    """


class DoiTuong:
    TABLE_NAME = 'DoiTuong'
    DOI_TUONG_ID = 'DoiTuong_Id'
    MA_DOI_TUONG = 'MaDoiTuong'
    TEN_DOI_TUONG = 'TenDoiTuong'
    GIOI_HAN_1 = 'GioiHan_1'
    TY_LE_1 = 'TyLe_1'
    TY_LE_2 = 'TyLe_2'

    STRUCTURE = [
        (DOI_TUONG_ID, "INTEGER PRIMARY KEY"),
        (MA_DOI_TUONG, "TEXT"),
        (TEN_DOI_TUONG, "TEXT"),
        (GIOI_HAN_1, "REAL"),
        (TY_LE_1, "REAL"),
        (TY_LE_2, "REAL")
    ]
    CONSTRAINTS = []

    SOURCE_QUERY = f"""
        SELECT DoiTuong_Id, MaDoiTuong, TenDoiTuong, GioiHan_1, TyLe_1, TyLe_2 
        FROM DM_DoiTuong 
        where tamngung=0
    """


class ICD:
    TABLE_NAME = 'ICD'
    MA_ICD = 'MaICD'
    TEN_ICD = 'TenICD'

    STRUCTURE = [
        (MA_ICD, "TEXT PRIMARY KEY"),
        (TEN_ICD, "TEXT")
    ]
    CONSTRAINTS = []

    SOURCE_QUERY = f"""
        SELECT distinct MaICD, TenICD 
        FROM DM_ICD where tamngung=0
    """


class DM_Duoc:
    TABLE_NAME = 'DM_Duoc'
    DUOC_ID = 'Duoc_Id'
    MA_DUOC = 'MaDuoc'
    TEN_DUOC_DAY_DU = 'TenDuocDayDu'
    DON_GIA = 'DonGia'
    TEN_DON_VI_TINH = 'TenDonViTinh'
    DICTIONARY_NAME = 'Dictionary_Name'
    PHAMVI = 'PhamVi'

    STRUCTURE = [
        (DUOC_ID, "INTEGER PRIMARY KEY"),
        (MA_DUOC, "TEXT"),
        (TEN_DUOC_DAY_DU, "TEXT"),
        (TEN_DON_VI_TINH, "TEXT"),
        (DICTIONARY_NAME, "TEXT"),
        (DON_GIA, "REAL"),
        (PHAMVI, "TEXT"),
    ]
    CONSTRAINTS = []

    SOURCE_QUERY = f"""
    SELECT * 
    FROM (    
        SELECT 
            duoc.Duoc_Id, MaDuoc, TenDuocDayDu, DonViTinh, Dictionary_Name, chungtu.DonGiaVon as DonGia, duoc.PhamVi
        FROM 
            DM_Duoc duoc
            outer apply(select top 1 * from ChungTuSoLoNhap ct where ct.Duoc_Id=duoc.Duoc_Id order by NgayNhap desc) chungtu
            join Lst_Dictionary dic on dic.Dictionary_Id=duoc.DuongDung_Id
        WHERE
            duoc.TamNgung=0 AND duoc.PhamVi='BV'

        UNION ALL

        SELECT duoc.Duoc_Id, MaDuoc, TenDuocDayDu, DonViTinh,Dictionary_Name,gia.DonGiaBan as DonGia,duoc.PhamVi
        FROM 
            DM_Duoc duoc
            outer apply(select top 1 * from Duoc_SoLoNhap_GiaBan giaban where giaban.duoc_id=duoc.Duoc_Id) gia
            join Lst_Dictionary dic on dic.Dictionary_Id=duoc.DuongDung_Id
        WHERE 
            duoc.TamNgung=0 AND duoc.PhamVi='NT'
    ) tmp
    WHERE tmp.DonGia is not null;
    """


class PhongBan:
    TABLE_NAME = 'PhongBan'
    PHONG_BAN_ID = 'PhongBan_Id'
    MA_PHONG_BAN = 'MaPhongBan'
    TEN_PHONG_BAN = 'TenPhongBan'

    STRUCTURE = [
        (PHONG_BAN_ID, "INTEGER PRIMARY KEY"),
        (MA_PHONG_BAN, "TEXT"),
        (TEN_PHONG_BAN, "TEXT")
    ]
    CONSTRAINTS = []

    SOURCE_QUERY = f"""
        SELECT PhongBan_Id, MaPhongBan, TenPhongBan
        FROM DM_PhongBan where TamNgung=0
    """


class NhomDichVu:
    TABLE_NAME = 'NhomDichVu'
    NHOM_DICH_VU_ID = 'NhomDichVu_Id'
    TEN_NHOM_DICH_VU = 'TenNhomDichVu'

    STRUCTURE = [
        (NHOM_DICH_VU_ID, "INTEGER PRIMARY KEY"),
        (TEN_NHOM_DICH_VU, "TEXT")
    ]
    CONSTRAINTS = []

    SOURCE_QUERY = f"""
        SELECT NhomDichVu_Id, TenNhomDichVu 
        FROM DM_NhomDichVu where TamNgung=0
    """


class DMDichVu:
    TABLE_NAME = 'DichVu'
    DICH_VU_ID = 'DichVu_Id'
    INPUT_CODE = 'InputCode'
    NHOM_DICH_VU_ID = 'NhomDichVu_Id'
    TEN_DICH_VU = 'TenDichVu'
    TEN_KHONG_DAU = 'TenKhongDau'

    STRUCTURE = [
        (DICH_VU_ID, "INTEGER PRIMARY KEY"),
        (INPUT_CODE, "TEXT"),
        (TEN_DICH_VU, "TEXT"),
        (TEN_KHONG_DAU, "TEXT"),
        (NHOM_DICH_VU_ID, "INTEGER"),
    ]
    # Ràng buộc khoá ngoại
    CONSTRAINTS = [
        f"FOREIGN KEY ({NHOM_DICH_VU_ID}) REFERENCES {NhomDichVu.TABLE_NAME} ({NhomDichVu.NHOM_DICH_VU_ID})"
    ]

    SOURCE_QUERY = f"""
        SELECT DichVu_Id, InputCode, TenDichVu, TenKhongDau,  NhomDichVu_Id
        FROM DM_DichVu where TamNgung=0
    """


class LoaiGia:
    TABLE_NAME = 'LoaiGia'
    LOAI_GIA_ID = 'LoaiGia_Id'
    MA_LOAI_GIA = 'MaLoaiGia'
    TEN_LOAI_GIA = 'TenLoaiGia'

    STRUCTURE = [
        (LOAI_GIA_ID, "INTEGER PRIMARY KEY"),
        (MA_LOAI_GIA, "TEXT"),
        (TEN_LOAI_GIA, "TEXT")
    ]
    CONSTRAINTS = []

    SOURCE_QUERY = f"""
        SELECT LoaiGia_Id, MaLoaiGia, TenLoaiGia
        FROM DM_LoaiGia where TamNgung=0
    """


class GiaDichVu:
    TABLE_NAME = 'GiaDichVu'
    DICH_VU_ID = 'DichVu_Id'
    LOAI_GIA_ID = 'LoaiGia_Id'
    DON_GIA = 'DonGia'

    STRUCTURE = [
        (DICH_VU_ID, "INTEGER"),
        (LOAI_GIA_ID, "INTEGER"),
        (DON_GIA, "REAL")
    ]
    # Khoá chính phức hợp và khoá ngoại
    CONSTRAINTS = [
        f"PRIMARY KEY ({DICH_VU_ID}, {LOAI_GIA_ID})",
        f"FOREIGN KEY ({DICH_VU_ID}) REFERENCES {DMDichVu.TABLE_NAME} ({DMDichVu.DICH_VU_ID})",
        f"FOREIGN KEY ({LOAI_GIA_ID}) REFERENCES {LoaiGia.TABLE_NAME} ({LoaiGia.LOAI_GIA_ID})"
    ]

    SOURCE_QUERY = f"""
        SELECT DichVu_Id, LoaiGia_Id, DonGia
        FROM DM_DichVu_DonGia where TamNgung=0
    """


class PhongBanDichVu:
    TABLE_NAME = 'PhongBanDichVu'
    DICH_VU_ID = 'DichVu_Id'
    PHONG_BAN_ID = 'PhongBan_Id'
    PHONG_BAN_DICH_VU_ID = 'PhongBan_DichVu_Id'

    STRUCTURE = [
        (DICH_VU_ID, "INTEGER"),
        (PHONG_BAN_ID, "INTEGER"),
        (PHONG_BAN_DICH_VU_ID, "INTEGER")
    ]
    CONSTRAINTS = [
        f"PRIMARY KEY ({DICH_VU_ID}, {PHONG_BAN_ID})",
        f"FOREIGN KEY ({DICH_VU_ID}) REFERENCES {DMDichVu.TABLE_NAME} ({DMDichVu.DICH_VU_ID})",
        f"FOREIGN KEY ({PHONG_BAN_ID}) REFERENCES {PhongBan.TABLE_NAME} ({PhongBan.PHONG_BAN_ID})"
    ]

    SOURCE_QUERY = f"""
        SELECT DichVu_Id, PhongBan_Id, PhongBan_DichVu_Id
        FROM DM_PhongBan_DichVu
    """


class DoiTuongLoaiGia:
    TABLE_NAME = 'DoiTuongLoaiGia'
    DOI_TUONG_ID = 'DoiTuong_Id'
    LOAI_GIA_ID = 'LoaiGia_Id'
    DOI_TUONG_LOAI_GIA_ID = 'DoiTuong_LoaiGia_Id'
    DO_UU_TIEN = 'DoUuTien'

    STRUCTURE = [
        (DOI_TUONG_ID, "INTEGER"),
        (LOAI_GIA_ID, "INTEGER"),
        (DOI_TUONG_LOAI_GIA_ID, "INTEGER"),
        (DO_UU_TIEN, "INTEGER")
    ]
    CONSTRAINTS = [
        f"PRIMARY KEY ({DOI_TUONG_ID}, {LOAI_GIA_ID})",
        f"FOREIGN KEY ({DOI_TUONG_ID}) REFERENCES {DoiTuong.TABLE_NAME} ({DoiTuong.DOI_TUONG_ID})",
        f"FOREIGN KEY ({LOAI_GIA_ID}) REFERENCES {LoaiGia.TABLE_NAME} ({LoaiGia.LOAI_GIA_ID})"
    ]

    SOURCE_QUERY = f"""
        SELECT DoiTuong_Id, LoaiGia_Id,  DoiTuong_LoaiGia_Id, DoUuTien
        FROM DM_DoiTuong_LoaiGia
    """