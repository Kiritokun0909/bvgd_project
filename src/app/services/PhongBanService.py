from app.services.execute_query import fetch_one_row, fetch_all_rows
from app.services.schema import Schema

TBL = Schema.PhongBan

def get_list_phong_ban() -> list[tuple] | None:
    data = fetch_all_rows(
        query=f'SELECT PhongBan_Id, MaPhongBan, TenPhongBan '
              f'FROM {TBL.TABLE_NAME} ',
        params= None
    )

    return data

if __name__ == '__main__':
    data = get_list_phong_ban()

    for i in range(len(data)):
        print(f'[{i}]:', data[i])