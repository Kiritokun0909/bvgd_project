from app.services.execute_query import fetch_one_row, fetch_all_rows
from app.services.schema import Schema

TBL_NHOM_DICH_VU = Schema.NhomDichVu

def get_all_nhom_dich_vu() -> list[tuple] | None:
    data = fetch_all_rows(
        query=f'SELECT NhomDichVu_Id, TenNhomDichVu FROM NhomDichVu ',
        params= None
    )

    return data


def get_nhom_dich_vu_by_ma_doi_tuong(ma_doi_tuong: str) -> list[tuple] | None:
    data = fetch_all_rows(
        query=f"""  
            SELECT DISTINCT
                T6.{Schema.NhomDichVu.NHOM_DICH_VU_ID}
                , T6.{Schema.NhomDichVu.TEN_NHOM_DICH_VU}
            FROM
                {Schema.DoiTuong.TABLE_NAME} AS T1
            JOIN
                {Schema.DoiTuongLoaiGia.TABLE_NAME} AS T2 ON T1.{Schema.DoiTuong.DOI_TUONG_ID} = T2.{Schema.DoiTuong.DOI_TUONG_ID}
            JOIN
                {Schema.LoaiGia.TABLE_NAME} AS T3 ON T2.{Schema.DoiTuongLoaiGia.LOAI_GIA_ID} = T3.{Schema.LoaiGia.LOAI_GIA_ID}
            JOIN
                {Schema.GiaDichVu.TABLE_NAME} AS T4 ON T3.{Schema.LoaiGia.LOAI_GIA_ID} = T4.{Schema.GiaDichVu.LOAI_GIA_ID}
            JOIN
                {Schema.DMDichVu.TABLE_NAME} AS T5 ON T4.{Schema.GiaDichVu.DICH_VU_ID} = T5.{Schema.DMDichVu.DICH_VU_ID}
            JOIN
                {Schema.NhomDichVu.TABLE_NAME} AS T6 ON T5.{Schema.DMDichVu.NHOM_DICH_VU_ID} = T6.{Schema.NhomDichVu.NHOM_DICH_VU_ID}
            WHERE
                T1.{Schema.DoiTuong.DOI_TUONG_ID} = ?	
            ORDER BY
                T6.{Schema.NhomDichVu.NHOM_DICH_VU_ID} ASC;
            """,
        params= (ma_doi_tuong,)
    )

    return data


if __name__ == '__main__':
    data = get_nhom_dich_vu_by_ma_doi_tuong('50')

    for i in range(len(data)):
        print(f'[{i}]:', data[i])


