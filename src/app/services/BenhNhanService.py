from app.services.execute_query import fetch_one_row
from app.services.schema import Schema

TBL = Schema.BenhNhan

def get_benh_nhan_by_id(ma_y_te: str) -> tuple:
    data = fetch_one_row(
        query=f'SELECT SoVaoVien, TenBenhNhan, GioiTinh, NamSinh, SoDienThoai, DiaChi'
              f' FROM BenhNhan WHERE SoVaoVien = ?',
        params=(ma_y_te,)
    )

    return data

if __name__ == '__main__':
    data = get_benh_nhan_by_id('11023278')
    print(data)