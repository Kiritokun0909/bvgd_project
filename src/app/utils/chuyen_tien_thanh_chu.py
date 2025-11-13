def doc_so_ba_chu_so(so):
    """Đọc một số có tối đa 3 chữ số."""
    don_vi = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    muoi = ["", "mười", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]

    so_str = str(int(so)).zfill(3)

    # Chữ số hàng trăm
    chu_so_tram = int(so_str[0])

    # Chữ số hàng chục và hàng đơn vị
    chu_so_chuc_don_vi = int(so_str[1:])
    chu_so_chuc = int(so_str[1])
    chu_so_don_vi = int(so_str[2])

    ket_qua = ""

    # Xử lý hàng trăm
    if chu_so_tram != 0:
        ket_qua += don_vi[chu_so_tram] + " trăm "
        if chu_so_chuc_don_vi == 0:
            return ket_qua.strip()  # Ví dụ: "bốn trăm"

    # Xử lý hàng chục và đơn vị
    if chu_so_chuc_don_vi != 0:
        if chu_so_tram != 0 and chu_so_chuc == 0:
            # Ví dụ: 105 - một trăm lẻ năm
            ket_qua += "lẻ "
        elif chu_so_chuc == 1:
            # Ví dụ: 1x - mười x
            ket_qua += "mười "
        elif chu_so_chuc > 1:
            # Ví dụ: 2x - hai mươi x
            ket_qua += muoi[chu_so_chuc].split()[0] + " mươi "  # Chỉ lấy "hai", "ba",...

        # Xử lý hàng đơn vị
        if chu_so_chuc_don_vi < 10 and chu_so_chuc > 0:
            # Ví dụ: 10, 20... - không cần đọc đơn vị
            if chu_so_don_vi != 0:
                ket_qua += don_vi[chu_so_don_vi]  # Ví dụ: "mười hai"
        elif chu_so_don_vi != 0:
            if chu_so_don_vi == 5 and chu_so_chuc != 0 and chu_so_chuc != 1:
                # Ví dụ: 25 - hai mươi lăm (khác với năm)
                ket_qua += "lăm"
            elif chu_so_don_vi == 1 and chu_so_chuc > 1:
                # Ví dụ: 21 - hai mươi mốt (khác với một)
                ket_qua += "mốt"
            else:
                ket_qua += don_vi[chu_so_don_vi]  # Ví dụ: "một", "hai",...

    return ket_qua.strip()


def chuyen_tien_thanh_chu(so_tien):
    """Chuyển đổi số tiền thành chữ (Tiếng Việt)."""

    if not isinstance(so_tien, (int, float)):
        try:
            so_tien = float(so_tien)
        except ValueError:
            return "**Lỗi:** Giá trị không hợp lệ."

    if so_tien < 0:
        return "**Lỗi:** Số tiền phải là số dương."
    if so_tien == 0:
        return "Không đồng"

    # Làm tròn để tránh lỗi dấu phẩy động
    so_tien_str = f"{so_tien:.2f}"

    # Tách phần nguyên và phần thập phân (nếu có)
    phan_nguyen_str, *phan_thap_phan_list = so_tien_str.split('.')
    phan_thap_phan_str = phan_thap_phan_list[0] if phan_thap_phan_list else '00'

    phan_nguyen = int(phan_nguyen_str)

    # 1. Đọc phần nguyên
    trieu_ty = ["", "nghìn", "triệu", "tỷ"]
    chuoi_ket_qua = []

    # Chia số nguyên thành các nhóm 3 chữ số từ phải sang trái
    phan_nguyen_nguoc = phan_nguyen_str[::-1]
    nhom_ba_chu_so = [phan_nguyen_nguoc[i:i + 3][::-1] for i in range(0, len(phan_nguyen_nguoc), 3)]
    nhom_ba_chu_so.reverse()

    # Đọc từng nhóm 3 chữ số
    co_doc_ty = False

    for i, nhom in enumerate(nhom_ba_chu_so):
        nhom_int = int(nhom)

        # Chỉ đọc nhóm 3 chữ số nếu nó khác 0
        if nhom_int != 0:
            # Đọc nhóm
            chuoi = doc_so_ba_chu_so(nhom_int)

            # Thêm đơn vị (nghìn, triệu, tỷ)
            don_vi_index = len(nhom_ba_chu_so) - 1 - i

            # Xử lý trường hợp "tỷ" (phải là số đầu tiên)
            if don_vi_index % 4 == 3:  # Đây là nhóm của "tỷ"
                chuoi_ket_qua.append(chuoi + " tỷ")
                co_doc_ty = True
            elif don_vi_index % 4 == 0:
                # Nếu không phải tỷ, thêm đơn vị (nghìn, triệu)
                chuoi_ket_qua.append(chuoi + " " + trieu_ty[don_vi_index % 4])
            else:
                # Trường hợp: tỷ, nghìn tỷ, triệu tỷ,...
                # Ở đây tập trung vào: nghìn, triệu, tỷ.
                # Chuỗi này xử lý các nhóm nhỏ hơn tỷ: nghìn, triệu, nghìn.

                # Ví dụ: 1.000.000.000.000 (một ngàn tỷ)
                # Đơn vị: nghìn, triệu, nghìn, đồng

                # Xử lý các nhóm 3 số nhỏ hơn tỷ, hoặc nhóm sau tỷ
                if don_vi_index % 4 == 1:
                    chuoi_ket_qua.append(chuoi + " nghìn")
                elif don_vi_index % 4 == 2:
                    chuoi_ket_qua.append(chuoi + " triệu")
                elif don_vi_index % 4 == 0 and don_vi_index > 0:
                    # Sau khi đọc tỷ (ví dụ: một tỷ, một trăm triệu)
                    chuoi_ket_qua.append(chuoi)

    # Thêm "đồng" vào cuối phần nguyên
    if phan_nguyen > 0:
        # Lấy phần nguyên sau khi xử lý các đơn vị lớn
        chuoi_doc_nguyen = " ".join(chuoi_ket_qua).strip()

        # Xử lý việc thừa "không nghìn", "không triệu" (do các nhóm 3 số bằng 0)
        chuoi_doc_nguyen = chuoi_doc_nguyen.replace("không nghìn", "")
        chuoi_doc_nguyen = chuoi_doc_nguyen.replace("không triệu", "")

        chuoi_doc_nguyen = chuoi_doc_nguyen.strip()

        if chuoi_doc_nguyen:
            chuoi_doc_nguyen += " đồng"

    else:
        chuoi_doc_nguyen = ""

    # 2. Đọc phần thập phân (nếu khác 0)
    phan_thap_phan = int(phan_thap_phan_str)
    chuoi_doc_thap_phan = ""

    if phan_thap_phan > 0:
        if phan_thap_phan_str[0] == '0' and phan_thap_phan_str[1] != '0':
            # Ví dụ: 0.05 -> lẻ năm
            chuoi_doc_thap_phan = " lẻ " + doc_so_ba_chu_so(phan_thap_phan) + " xu"
        else:
            # Ví dụ: 0.50 -> năm mươi xu, 0.23 -> hai mươi ba xu
            chuoi_doc_thap_phan = " và " + doc_so_ba_chu_so(phan_thap_phan) + " xu"

    # Kết hợp và định dạng
    ket_qua_cuoi = (chuoi_doc_nguyen + chuoi_doc_thap_phan).strip()

    # Viết hoa chữ cái đầu tiên
    if ket_qua_cuoi:
        return ket_qua_cuoi[0].upper() + ket_qua_cuoi[1:]
    else:
        return ""

if __name__ == '__main__':
    # --- Ví dụ minh họa ---
    print("## Ví dụ:")
    print(f"23.500.000,00 -> **{chuyen_tien_thanh_chu(23500000)}**")
    print(f"123.456,78 -> **{chuyen_tien_thanh_chu(123456.78)}**")
    print(f"1.000.000 -> **{chuyen_tien_thanh_chu(1000000)}**")
    print(f"500 -> **{chuyen_tien_thanh_chu(500)}**")
    print(f"201.000.000 -> **{chuyen_tien_thanh_chu(201000000)}**")
    print(f"12.345.678.901,05 -> **{chuyen_tien_thanh_chu(12345678901.05)}**")