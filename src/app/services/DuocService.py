from app.services.execute_query import fetch_one_row, fetch_all_rows
from app.services.schema import Schema
from app.services.DoiTuongService import get_doi_tuong_by_id

TBL = Schema.DM_Duoc

def get_list_duoc(keyword: str = '', doi_tuong_id: str = '20') -> list:
    doi_tuong_data = get_doi_tuong_by_id(doi_tuong_id)
    gioi_han = doi_tuong_data[3]
    pham_vi = 'BV'
    if gioi_han is None or gioi_han == 0:
        pham_vi = 'NT'

    data = fetch_all_rows(
        query=f"""  
        SELECT 
            Duoc_Id
            , MaDuoc
            , TenDuocDayDu
            , DonGia
            , TenDonViTinh
            , Dictionary_Name AS CachDung
        FROM 
            {TBL.TABLE_NAME}
        WHERE 
            Dictionary_Name IS NOT NULL --- Nếu null là vat tu y te
            AND (TenDuocDayDu LIKE ? OR MaDuoc LIKE ?)
            AND PhamVi = ? ;
        """,
        params= (keyword + '%', keyword + '%', pham_vi,)
    )

    return data

def get_duoc_by_id(ma_duoc: str) -> tuple:
    data = fetch_one_row(
        query=f"""   
        SELECT 
            Duoc_Id
            , MaDuoc
            , TenDuocDayDu
            , DonGia
            , TenDonViTinh
            , Dictionary_Name AS CachDung
        FROM 
            {TBL.TABLE_NAME}
        WHERE 
            Dictionary_Name IS NOT NULL --- Nếu null là vat tu y te
            AND MaDuoc = ? ;
        """,
        params=(ma_duoc, )
    )

    return data

def get_duoc_by_duoc_id(duoc_id: str) -> tuple:
    data = fetch_one_row(
        query=f"""   
        SELECT 
            Duoc_Id
            , MaDuoc
            , TenDuocDayDu
            , DonGia
            , TenDonViTinh
            , Dictionary_Name AS CachDung
        FROM 
            {TBL.TABLE_NAME}
        WHERE 
            Dictionary_Name IS NOT NULL --- Nếu null là vat tu y te
            AND Duoc_Id = ? ;
        """,
        params=(duoc_id, )
    )

    return data

if __name__ == '__main__':
    data = get_list_duoc(keyword='tab', doi_tuong_id='20')
    for i in range(len(data)):
        print(f'[{i}]:', data[i])

    data = get_duoc_by_id('TabT4')
    print(data)
