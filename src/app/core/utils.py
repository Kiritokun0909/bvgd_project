from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors


# Hàm lấy style alignment giữ nguyên không đổi
def get_align_style(font_name, font_size, align_code='L'):
    align_map = {'L': TA_LEFT, 'C': TA_CENTER, 'R': TA_RIGHT}
    return ParagraphStyle(
        name=f'Style_{align_code}',
        fontName=font_name,
        fontSize=font_size,
        leading=font_size + 2,
        alignment=align_map.get(align_code.upper(), TA_LEFT),
        spaceAfter=0,
    )


def draw_multi_column_table(c, x_start, y_start,
                            table_data, col_widths, col_aligns,
                            font, font_size,
                            # --- CÁC THAM SỐ MỚI ---
                            border_color=colors.black,  # Màu viền (None để ẩn)
                            border_width=0.5,  # Độ dày viền
                            header_bg_color=None,  # Màu nền dòng tiêu đề (dòng 0)
                            padding=2  # Khoảng đệm trong ô
                            ):
    """
    Hàm vẽ bảng đa năng có hỗ trợ màu nền và viền.
    """
    processed_data = []

    # 1. Chuẩn bị Styles
    styles = {
        'L': get_align_style(font, font_size, 'L'),
        'C': get_align_style(font, font_size, 'C'),
        'R': get_align_style(font, font_size, 'R')
    }

    # 2. Xử lý dữ liệu thành Paragraph
    for row_idx, row in enumerate(table_data):
        processed_row = []
        for col_idx, cell_text in enumerate(row):
            align = col_aligns[col_idx] if col_idx < len(col_aligns) else 'L'

            # Tự động in đậm dòng tiêu đề (row_idx == 0) nếu có màu nền header
            # Bạn có thể bỏ logic này nếu muốn kiểm soát font từ bên ngoài
            current_font = font

            style = styles.get(align.upper(), styles['L'])
            # Clone style để tránh ảnh hưởng các lần gọi khác (nếu cần chỉnh sửa sâu hơn)

            p = Paragraph(str(cell_text), style)
            processed_row.append(p)
        processed_data.append(processed_row)

    # 3. Tạo bảng
    table = Table(processed_data, colWidths=col_widths)

    # 4. Định nghĩa danh sách các lệnh Style
    style_cmds = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Căn trên theo chiều dọc

        # Padding: Khi có viền, cần padding để chữ không dính vào viền
        ('LEFTPADDING', (0, 0), (-1, -1), padding),
        ('RIGHTPADDING', (0, 0), (-1, -1), padding),
        ('TOPPADDING', (0, 0), (-1, -1), padding),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
    ]

    # --- XỬ LÝ VIỀN ---
    if border_width > 0 and border_color is not None:
        # GRID: Vẽ toàn bộ lưới (viền ngoài + viền trong)
        style_cmds.append(('GRID', (0, 0), (-1, -1), border_width, border_color))
    else:
        # Nếu không muốn viền, để viền trắng hoặc độ dày 0
        style_cmds.append(('GRID', (0, 0), (-1, -1), 0, colors.white))

    # --- XỬ LÝ MÀU NỀN HEADER ---
    if header_bg_color is not None:
        # BACKGROUND cho dòng đầu tiên (row 0) từ cột 0 đến cột cuối (-1)
        style_cmds.append(('BACKGROUND', (0, 0), (-1, 0), header_bg_color))

        # Thường khi có nền header, chữ nên màu trắng hoặc đen đậm.
        # Ở đây ví dụ set màu chữ dòng đầu là màu trắng nếu nền tối (tuỳ chọn)
        # style_cmds.append(('TEXTCOLOR', (0, 0), (-1, 0), colors.white))

    # Áp dụng style
    table.setStyle(TableStyle(style_cmds))

    # 5. Tính toán và vẽ
    w, h = table.wrapOn(c, 0, 0)
    y_position = y_start - h
    table.drawOn(c, x_start, y_position)

    return y_position