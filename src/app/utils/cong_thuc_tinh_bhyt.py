from app.services.DoiTuongService import get_doi_tuong_by_id

def tinh_tien_mien_giam(tong_tien: float,
                        tien_dich_vu: float,
                        ma_doi_tuong: str) -> float:
    doi_tuong_data = get_doi_tuong_by_id(ma_doi_tuong)
    gioi_han = doi_tuong_data[3]
    ty_le_2 = doi_tuong_data[5]

    if gioi_han is None or gioi_han == 0:
        return 0

    if tong_tien <= float(gioi_han):
        return tien_dich_vu

    if ty_le_2 is None:
        return 0

    tien_mien_giam = tien_dich_vu * float(ty_le_2)
    return tien_mien_giam

if __name__ == '__main__':
    mien_giam = tinh_tien_mien_giam(315000, 30000, '50')
    print(mien_giam)