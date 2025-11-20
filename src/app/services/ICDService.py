from app.services.execute_query import fetch_one_row, fetch_all_rows
from app.services.schema import Schema

TBL = Schema.ICD

def get_list_icd(keyword: str = '') -> list[tuple] | None:
    data = fetch_all_rows(
        query=f"""  SELECT 
                        MaICD
                       , TenICD
                    FROM {TBL.TABLE_NAME}
                    WHERE MaICD LIKE ?
                    LIMIT 100
        """,
        params= (keyword + '%',)
    )

    return data

def get_icd_name(ma_icd: str) -> tuple | None:
    data = fetch_one_row(
        query=f'SELECT MaICD, TenICD FROM {TBL.TABLE_NAME} WHERE MaICD = ?',
        params=(ma_icd, )
    )

    return data

if __name__ == '__main__':
    data = get_list_icd()
    for i in range(len(data)):
        print(f'[{i}]:', data[i])

    data = get_icd_name('A00')
    print(data)
