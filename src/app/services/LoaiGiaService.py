from app.services.DichVuService import TBL_DOI_TUONG_LOAI_GIA
from app.services.execute_query import fetch_one_row, fetch_all_rows
from app.services.schema import Schema

TBL_LOAI_GIA = Schema.LoaiGia
TBL_DOI_TUONG_LOAI_GIA = Schema.DoiTuongLoaiGia

def get_list_loai_gia() -> list[tuple] | None:
    data = fetch_all_rows(
        query=f'SELECT LoaiGia_Id, MaLoaiGia, TenLoaiGia '
              f'FROM {TBL_LOAI_GIA.TABLE_NAME} ',
        params= None
    )

    return data

def get_list_loai_gia_by_doi_tuong_id(doi_tuong_id: str) -> list[tuple] | None:
    data = fetch_all_rows(
        query=f"""  
            SELECT
                lg.LoaiGia_Id, lg.MaLoaiGia, lg.TenLoaiGia, dtlg.DoiTuong_Id
            FROM 
                {TBL_DOI_TUONG_LOAI_GIA.TABLE_NAME} dtlg
                JOIN {TBL_LOAI_GIA.TABLE_NAME} lg ON dtlg.LoaiGia_Id = lg.LoaiGia_Id
            WHERE 
                dtlg.DoiTuong_Id = ?
        """,
        params= (doi_tuong_id, )
    )

    return data

def get_list_loai_gia_by_dich_vu_id(doi_tuong_id: str, dich_vu_id: str) -> list[tuple] | None:
    data = fetch_all_rows(
        query=f"""  
            SELECT 
                lg.{Schema.LoaiGia.LOAI_GIA_ID}
                , lg.{Schema.LoaiGia.TEN_LOAI_GIA}
                , dtlg.{Schema.DoiTuongLoaiGia.DO_UU_TIEN} 
            FROM
                {Schema.LoaiGia.TABLE_NAME} lg
                JOIN {Schema.DoiTuongLoaiGia.TABLE_NAME} dtlg ON lg.{Schema.LoaiGia.LOAI_GIA_ID} = dtlg.{Schema.DoiTuongLoaiGia.LOAI_GIA_ID}
                JOIN {Schema.GiaDichVu.TABLE_NAME} gia ON lg.{Schema.LoaiGia.LOAI_GIA_ID} = gia.{Schema.GiaDichVu.LOAI_GIA_ID}
            WHERE 
                gia.{Schema.GiaDichVu.DICH_VU_ID} = ? AND dtlg.{Schema.DoiTuongLoaiGia.DOI_TUONG_ID} = ?
            ORDER BY
                dtlg.{Schema.DoiTuongLoaiGia.DO_UU_TIEN} ASC
        """,
        params=(dich_vu_id, doi_tuong_id, )
    )

    return data

if __name__ == '__main__':
    # data = get_list_loai_gia()
    # data = get_list_loai_gia_by_doi_tuong_id('50')
    data = get_list_loai_gia_by_dich_vu_id('50', '3876')

    for i in range(len(data)):
        print(f'[{i}]:', data[i])