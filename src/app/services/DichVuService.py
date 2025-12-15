from app.services.execute_query import fetch_one_row, fetch_all_rows
from app.services.schema import Schema

TBL_NHOM_DICH_VU = Schema.NhomDichVu
TBL_DICH_VU = Schema.DMDichVu
TBL_DOI_TUONG_LOAI_GIA = Schema.DoiTuongLoaiGia

def get_list_dich_vu_by_ma_nhom_dich_vu(ma_doi_tuong: str, ma_nhom_dich_vu: str) -> list:
    data = fetch_all_rows(
        query=f"""  
            SELECT DISTINCT
                T5.{Schema.DMDichVu.DICH_VU_ID}
                , T5.{Schema.DMDichVu.INPUT_CODE}
                , T5.{Schema.DMDichVu.TEN_DICH_VU}
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
            WHERE
                T1.{Schema.DoiTuong.DOI_TUONG_ID} = ? AND T5.{Schema.DMDichVu.NHOM_DICH_VU_ID} = ?
            ORDER BY
                T5.{Schema.DMDichVu.DICH_VU_ID} ASC;
            """,
        params= (ma_doi_tuong, ma_nhom_dich_vu,)
    )

    return data

def get_list_dich_vu_by_keyword(doi_tuong_id: str, keyword: str) -> list:
    keyword = keyword.lower()

    data = fetch_all_rows(
        query=f"""  
            SELECT DISTINCT
                T5.{Schema.DMDichVu.DICH_VU_ID}
                , T5.{Schema.DMDichVu.INPUT_CODE}
                , T5.{Schema.DMDichVu.TEN_DICH_VU}
                , T5.{Schema.DMDichVu.TEN_KHONG_DAU}
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
            WHERE
                T1.{Schema.DoiTuong.DOI_TUONG_ID} = ? AND 
                (T5.{Schema.DMDichVu.TEN_DICH_VU} LIKE ? OR T5.{Schema.DMDichVu.TEN_KHONG_DAU} LIKE ? )
            ORDER BY
                T5.{Schema.DMDichVu.DICH_VU_ID} ASC;
            """,
        params=(doi_tuong_id, keyword + '%', keyword + '%',)
    )

    return data

def get_dich_vu_by_input_code(doi_tuong_id: str, input_code: str) -> tuple:
    data = fetch_one_row(
        query=f"""  
            SELECT DISTINCT
                T5.{Schema.DMDichVu.DICH_VU_ID}
                , T5.{Schema.DMDichVu.INPUT_CODE}
                , T5.{Schema.DMDichVu.TEN_DICH_VU}
                , T5.{Schema.DMDichVu.NHOM_DICH_VU_ID}
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
            WHERE
                T1.{Schema.DoiTuong.DOI_TUONG_ID} = ? AND 
                T5.{Schema.DMDichVu.INPUT_CODE} LIKE ?
            """,
        params=(doi_tuong_id, input_code,)
    )

    return data

def get_dich_vu_by_dich_vu_id(doi_tuong_id: str, dich_vu_id: str) -> tuple:
    data = fetch_one_row(
        query=f"""  
            SELECT DISTINCT
                T5.{Schema.DMDichVu.DICH_VU_ID}
                , T5.{Schema.DMDichVu.INPUT_CODE}
                , T5.{Schema.DMDichVu.TEN_DICH_VU}
                , T5.{Schema.DMDichVu.NHOM_DICH_VU_ID}
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
            WHERE
                T1.{Schema.DoiTuong.DOI_TUONG_ID} = ? AND 
                T5.{Schema.DMDichVu.DICH_VU_ID} = ?
            """,
        params=(doi_tuong_id, dich_vu_id,)
    )

    return data

def get_gia_dich_vu(dich_vu_id: str, loai_gia_id: str) -> tuple:
    data = fetch_one_row(
        query=f"""  
            SELECT 
                {Schema.GiaDichVu.DON_GIA} 
            FROM 
                {Schema.GiaDichVu.TABLE_NAME}  
            WHERE 
                {Schema.GiaDichVu.DICH_VU_ID}  = ? 
                AND {Schema.GiaDichVu.LOAI_GIA_ID}  = ?  
        """,
        params=(dich_vu_id, loai_gia_id,)
    )

    return data

def get_noi_thuc_hien_dich_vu(dich_vu_id: str) -> list:
    data = fetch_all_rows(
        query=f"""  
            SELECT 
                pbdv.{Schema.PhongBanDichVu.PHONG_BAN_ID}
                , pb.{Schema.PhongBan.MA_PHONG_BAN}
                , pb.{Schema.PhongBan.TEN_PHONG_BAN}
            FROM {Schema.PhongBanDichVu.TABLE_NAME} pbdv 
                JOIN {Schema.PhongBan.TABLE_NAME} pb ON pb.{Schema.PhongBan.PHONG_BAN_ID} = pbdv.{Schema.PhongBanDichVu.PHONG_BAN_ID} 
            WHERE 
                pbdv.{Schema.PhongBanDichVu.DICH_VU_ID} = ?
            """,
        params=(dich_vu_id,)
    )

    return data


if __name__ == '__main__':
    # data = get_list_dich_vu_by_ma_nhom_dich_vu('50', '6')
    # data = get_list_dich_vu_by_keyword('50', 'Noi')
    # data = get_dich_vu_by_input_code('50', '778')
    # data = get_dich_vu_by_dich_vu_id('3876')
    # data = get_gia_dich_vu('3876', '27')
    # print(data)

    data = get_noi_thuc_hien_dich_vu('3876')

    for i in range(len(data)):
        print(f'[{i}]:', data[i])

        # data = get_dich_vu_by_id('')
        #
        # print(data)



