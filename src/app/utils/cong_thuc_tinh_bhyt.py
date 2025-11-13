from app.configs.table_dich_vu_configs import DOI_TUONG_FILE_PATH
from app.utils.utils import load_data_from_csv, get_first_row_data, unformat_currency_to_float
from app.utils.setting_loader import AppConfig

MLCS = AppConfig.LUONG_CO_SO
PHAN_TRAM_THANH_TOAN = AppConfig.PHAN_TRAM_THANH_TOAN

NGUONG_MIEN_CHI_TRA = MLCS * PHAN_TRAM_THANH_TOAN
doi_tuong_df = load_data_from_csv(DOI_TUONG_FILE_PATH)

def tinh_tien_mien_giam(tong_tien: float,
                        tien_dich_vu: float,
                        ma_doi_tuong: str) -> float:

    # Neu benh nhan có bhyt
    filter_df = doi_tuong_df[
        doi_tuong_df['MaDT'].astype(str).str
        .contains(ma_doi_tuong, na=False)
    ]
    doi_tuong = get_first_row_data(filter_df)
    ti_le_mien_giam = float(doi_tuong.get('PhanTramBHYT')) * 0.01

    if ti_le_mien_giam > 0:
        if tong_tien <= NGUONG_MIEN_CHI_TRA:
            return tien_dich_vu
        return tien_dich_vu * ti_le_mien_giam

    return 0