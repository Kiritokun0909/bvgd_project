import os
import json
import pandas as pd
from datetime import datetime
from app.utils.get_file_path import get_file_path

# Đường dẫn gốc chứa data json
DATA_DIR = get_file_path('data/collect')
EXPORT_DIR = get_file_path('data/exports')


def export_daily_report_to_excel(date_str):
    """
    Xuất dữ liệu ngày ra Excel.
    Cập nhật: Thêm đầy đủ Sinh hiệu (Mạch, Nhiệt, HA, SPO2...) và thông tin Hành chính.
    """
    day_dir = os.path.join(DATA_DIR, date_str)

    if not os.path.exists(day_dir):
        print(f"Không tìm thấy dữ liệu ngày {date_str}")
        return None

    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    # Khởi tạo danh sách
    list_drugs = []
    list_services = []
    list_invoices = []

    # Quét file JSON
    for filename in os.listdir(day_dir):
        if not filename.endswith('.json'):
            continue

        file_path = os.path.join(day_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Lỗi đọc file {filename}: {e}")
            continue

        # --- LẤY THÔNG TIN CHUNG (Meta Data) ---
        meta = data.get('meta_data', {})
        user_id = meta.get('user_id', '')
        user_name = meta.get('user_name', '')

        bills = data.get('bills', {})

        # --- SHEET 1: CHI TIẾT KHÁM & THUỐC (DRUG BILLS) ---
        # Đây là nơi chứa thông tin khám lâm sàng đầy đủ nhất
        drug_bill = bills.get('drug_bill')
        if drug_bill and 'ToaThuoc' in drug_bill:
            # Lấy thông tin sinh hiệu từ drug_bill (nếu Controller đã lưu)
            # Lưu ý: Các key này phải khớp với key trong file JSON bạn đã lưu
            vital_signs = {
                'Mạch (l/p)': drug_bill.get('Mach', ''),
                'Nhiệt độ (°C)': drug_bill.get('NhietDo', ''),
                'Huyết áp (mmHg)': drug_bill.get('HA', ''),
                'Nhịp thở (l/p)': drug_bill.get('NhipTho', ''),
                'Cân nặng (kg)': drug_bill.get('CanNang', ''),
                'Chiều cao (cm)': drug_bill.get('ChieuCao', ''),
                'SPO2 (%)': drug_bill.get('SPO2', ''),
                'Đường huyết': drug_bill.get('DuongHuyet', ''),
            }

            for drug in drug_bill['ToaThuoc']:
                row = {
                    # 1. Hành chính
                    'Mã BN': user_id,
                    'Tên Bệnh Nhân': user_name,
                    'Tuổi': drug_bill.get('Tuoi', ''),
                    'Giới Tính': drug_bill.get('GioiTinh', ''),
                    'Địa Chỉ': drug_bill.get('DiaChi', ''),
                    'BHYT': drug_bill.get('BHYT', ''),

                    # 2. Sinh hiệu & Lâm sàng (Thêm mới)
                    **vital_signs,  # Bung toàn bộ dict sinh hiệu vào đây

                    'Chẩn Đoán': drug_bill.get('ChanDoan', ''),
                    'Bác Sĩ': drug_bill.get('TenBacSi', ''),

                    # 3. Thông tin thuốc
                    'Mã Thuốc': drug.get('MaThuoc', ''),
                    'Tên Thuốc': drug.get('TenThuoc', ''),
                    'Số Lượng': drug.get('SoLuong', 0),

                    # 4. Cách dùng chi tiết
                    'Sáng': drug.get('Sang', ''),
                    'Trưa': drug.get('Trua', ''),
                    'Chiều': drug.get('Chieu', ''),
                    'Tối': drug.get('Toi', '')
                }
                list_drugs.append(row)

        # --- SHEET 2: DỊCH VỤ (SERVICE BILLS) ---
        service_bill = bills.get('service_bill')
        if service_bill and 'DichVu' in service_bill:
            # Lấy thông tin bệnh nhân từ phần dịch vụ (đề phòng trường hợp thuốc chưa có)
            bn_info_svc = service_bill.get('ThongTinBenhNhan', {})

            for service in service_bill['DichVu']:
                row = {
                    'Mã BN': user_id,
                    'Tên Bệnh Nhân': user_name,
                    'Tuổi': bn_info_svc.get('tuoi', ''),
                    'Giới Tính': bn_info_svc.get('gioi_tinh', ''),

                    'Bác Sĩ CĐ': service_bill.get('BacSi', ''),
                    'Chẩn Đoán': service_bill.get('ChanDoan', ''),

                    'Mã Dịch Vụ': service.get('MaDichVu', ''),
                    'Tên Dịch Vụ': service.get('TenDichVu', ''),
                    'Nơi Thực Hiện': service.get('NoiThucHien', ''),
                    'Số Lượng': service.get('SoLuong', 1),
                    'Đơn Giá': service.get('DonGia', 0),  # Nếu có lưu
                }
                list_services.append(row)

        # --- SHEET 3: HÓA ĐƠN (INVOICES) ---
        invoice = bills.get('invoice')
        if invoice:
            row = {
                'Mã BN': user_id,
                'Tên Bệnh Nhân': user_name,
                'Người Thu': invoice.get('NguoiThuTien', ''),
                'Thời Gian': invoice.get('NgayTao', date_str),
                'Tổng Tiền': invoice.get('TongTienThanhToan', 0),
                'Hình Thức TT': invoice.get('HinhThucThanhToan', ''),
                'Đơn Vị': invoice.get('TenDonVi', ''),
                'MST': invoice.get('MST', '')
            }
            list_invoices.append(row)

    # --- XUẤT FILE ---
    df_drugs = pd.DataFrame(list_drugs)
    df_services = pd.DataFrame(list_services)
    df_invoices = pd.DataFrame(list_invoices)

    # Sắp xếp
    if not df_drugs.empty:
        df_drugs.sort_values(by=['Tên Bệnh Nhân', 'Tên Thuốc'], inplace=True)
    if not df_services.empty:
        df_services.sort_values(by=['Tên Bệnh Nhân', 'Tên Dịch Vụ'], inplace=True)
    if not df_invoices.empty:
        df_invoices.sort_values(by=['Tên Bệnh Nhân'], inplace=True)

    # timestamp = datetime.now().strftime("%H%M%S")
    timestamp = ''
    output_filename = f"BaoCao_Ngay_{date_str}_{timestamp}.xlsx"
    output_path = os.path.join(EXPORT_DIR, output_filename)

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet Thuốc
            if not df_drugs.empty:
                df_drugs.to_excel(writer, sheet_name='Chi Tiết Thuốc & Khám', index=False)
                _auto_adjust_column_width(writer, df_drugs, 'Chi Tiết Thuốc & Khám')
            else:
                pd.DataFrame({'Info': ['Không có dữ liệu']}).to_excel(writer, sheet_name='Chi Tiết Thuốc & Khám',
                                                                      index=False)

            # Sheet Dịch Vụ
            if not df_services.empty:
                df_services.to_excel(writer, sheet_name='Chi Tiết Dịch Vụ', index=False)
                _auto_adjust_column_width(writer, df_services, 'Chi Tiết Dịch Vụ')
            else:
                pd.DataFrame({'Info': ['Không có dữ liệu']}).to_excel(writer, sheet_name='Chi Tiết Dịch Vụ',
                                                                      index=False)

            # Sheet Hóa Đơn
            if not df_invoices.empty:
                df_invoices.to_excel(writer, sheet_name='Tổng Hợp Doanh Thu', index=False)
                _auto_adjust_column_width(writer, df_invoices, 'Tổng Hợp Doanh Thu')
            else:
                pd.DataFrame({'Info': ['Không có dữ liệu']}).to_excel(writer, sheet_name='Tổng Hợp Doanh Thu',
                                                                      index=False)

        print(f"Xuất file thành công: {output_path}")
        return output_path

    except Exception as e:
        print(f"Lỗi khi ghi file Excel: {e}")
        return None


def _auto_adjust_column_width(writer, df, sheet_name):
    """Căn chỉnh độ rộng cột thông minh"""
    worksheet = writer.sheets[sheet_name]
    for i, col in enumerate(df.columns):
        sample_values = df[col].astype(str).head(50)
        max_len = max(
            sample_values.map(len).max() if not sample_values.empty else 0,
            len(str(col))
        ) + 3

        if max_len > 40: max_len = 40
        if max_len < 8: max_len = 8

        worksheet.column_dimensions[chr(65 + i)].width = max_len

def export_excel():
    today = datetime.now().strftime("%Y-%m-%d")
    export_daily_report_to_excel(today)

if __name__ == '__main__':
    export_excel()