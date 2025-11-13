import json
from datetime import datetime
import pandas as pd


def convert_benhnhan_data(input_data, df_danh_muc):
    """
    Chuyển đổi dữ liệu bệnh nhân từ định dạng đầu vào sang định dạng in ấn,
    sử dụng DataFrame để tra cứu tên nhóm dịch vụ.

    Args:
        input_data (dict): Dữ liệu JSON đầu vào.
        df_danh_muc (pd.DataFrame): DataFrame chứa danh mục nhóm dịch vụ
                                    (ít nhất phải có cột 'MaNhomDichVu' và 'TenNhomDichVu').

    Returns:
        dict: Dữ liệu đã chuyển đổi theo định dạng mong muốn.
    """

    # 1. Khai báo các giá trị mặc định/giả định
    default_info = {
        'SoYTe': 'SỞ Y TẾ TP.HCM',
        'TenBenhVien': 'BỆNH VIỆN ABC',
        # Lấy "nơi yêu cầu" làm tên phòng khám
        'PhongKham': input_data['ThongTinPhongKham'].get('noi_yeu_cau', 'Phòng Khám Đa Khoa'),
        'CSKH': '0123',
        'DoiTuong': f"{input_data['ThongTinBenhNhan'].get('doi_tuong', 'Không rõ')}",
        'NgayTao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'BacSi': 'Bs. Nguyễn Thị C',
    }

    # Lấy thông tin từ các phần chính của input_data
    tt_benhnhan = input_data.get('ThongTinBenhNhan', {})
    tt_phongkham = input_data.get('ThongTinPhongKham', {})
    tt_thanhtoan = input_data.get('ThanhToan', {})
    dich_vu_dang_ky = input_data.get('DichVuDangKy', [])

    # Chuẩn bị Dictionary tra cứu từ DataFrame
    try:
        # 🌟 Sử dụng cột 'MaDanhMuc' làm khóa tra cứu và 'TenDanhMuc' làm giá trị
        lookup_dict = df_danh_muc.set_index('MaDanhMuc')['TenDanhMuc'].to_dict()
    except KeyError:
        print("Lỗi: DataFrame danh mục phải có cột 'MaDanhMuc' và 'TenDanhMuc'.")
        lookup_dict = {}

    # 2. Xử lý phần Dịch Vụ và Gom nhóm
    grouped_services = {}
    for service in dich_vu_dang_ky:
        # MaNhomDichVu trong input_data tương ứng với MaDanhMuc trong df
        ma_nhom = service.get('MaNhomDichVu', 'KhongNhom')

        # 🌟 Tra cứu Tên Nhóm Dịch Vụ từ dictionary đã tạo
        # MaNhomDichVu trong input_data được dùng để tra cứu MaDanhMuc trong lookup_dict
        ten_nhom = lookup_dict.get(ma_nhom, f"NHÓM CHƯA XÁC ĐỊNH ({ma_nhom})")

        if ma_nhom not in grouped_services:
            grouped_services[ma_nhom] = {
                'MaNhomDichVu': ma_nhom,
                'TenNhomDichVu': ten_nhom,  # 👈 Đã sử dụng TenDanhMuc tra cứu
                'DSDichVu': []
            }

        # Chuyển đổi chi tiết dịch vụ
        grouped_services[ma_nhom]['DSDichVu'].append({
            "STT": str(len(grouped_services[ma_nhom]['DSDichVu']) + 1),
            "MaDichVu": service.get("MaDichVu", ""),
            "TenDichVu": service.get("TenDichVu", ""),
            "SoLuong": service.get("SoLuong", "1"),
            "NoiThucHien": service.get("NoiThucHien", "")
        })

    dich_vu_output = list(grouped_services.values())

    # 3. Xây dựng cấu trúc dữ liệu đầu ra
    output_data = {
        'SoYTe': default_info['SoYTe'],
        'TenBenhVien': default_info['TenBenhVien'],
        'PhongKham': default_info['PhongKham'],
        'CSKH': default_info['CSKH'],

        'MaYTe': tt_benhnhan.get('ma_y_te', ''),
        'MaBHYT': tt_benhnhan.get('so_bhyt', ''),
        'DoiTuong': default_info['DoiTuong'],
        'HoTen': tt_benhnhan.get('ho_ten', ''),
        'Tuoi': tt_benhnhan.get('tuoi', ''),
        'GioiTinh': tt_benhnhan.get('gioi_tinh', ''),
        'DiaChi': tt_benhnhan.get('dia_chi', ''),
        'SDT': tt_benhnhan.get('sdt', ''),

        'ChanDoan': tt_phongkham.get('chan_doan', ''),
        'GhiChu': tt_phongkham.get('ghi_chu', ''),
        # Lấy DonGiaDoanhThu của dịch vụ đầu tiên
        'SoTien': tt_thanhtoan.get('TongThanhTienDV', '0'),
        'TongBenhNhanTra': tt_thanhtoan.get('TongBenhNhanTT', '0'),

        'NgayTao': default_info['NgayTao'],
        'BacSi': default_info['BacSi'],

        'DichVu': dich_vu_output
    }

    return output_data