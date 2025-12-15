from app.services.execute_query import fetch_one_row, fetch_all_rows
from app.services.schema import Schema

TBL = Schema.DM_Duoc

def get_list_duoc(keyword: str = '') -> list:
    data = fetch_all_rows(
        query=f"""  SELECT 
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
                        AND TenDuocDayDu LIKE ? ;
        """,
        params= (keyword + '%',)
    )

    return data

def get_duoc_by_id(ma_duoc: str) -> tuple:
    data = fetch_one_row(
        query=f"""   SELECT 
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
        query=f"""   SELECT 
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
    data = get_list_duoc(keyword='tab')
    for i in range(len(data)):
        print(f'[{i}]:', data[i])

    data = get_duoc_by_id('TabT4')
    print(data)
