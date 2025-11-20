from app.services.execute_query import fetch_one_row, fetch_all_rows
from app.services.schema import Schema

TBL = Schema.DoiTuong

def get_list_doi_tuong() -> list[tuple] | None:
    data = fetch_all_rows(
        query=f'SELECT DoiTuong_Id, MaDoiTuong, TenDoiTuong '
              f'FROM {TBL.TABLE_NAME} ',
        params= None
    )

    return data

def get_doi_tuong_by_id(doi_tuong_id: str) -> tuple | None:
    data = fetch_one_row(
        query=f"""  
            SELECT 
                DoiTuong_Id, MaDoiTuong, TenDoiTuong, GioiHan_1, TyLe_1, TyLe_2
            FROM 
                {TBL.TABLE_NAME} 
            WHERE 
                {TBL.DOI_TUONG_ID} = ?
        """,
        params=(doi_tuong_id,)
    )

    return data

if __name__ == '__main__':
    data = get_list_doi_tuong()

    for i in range(len(data)):
        print(f'[{i}]:', data[i])

    data = get_doi_tuong_by_id(2)
    print(data)