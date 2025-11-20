import os
import sys
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

# Cấu hình Font mặc định
VIET_FONT = 'TimesNewRomanVN'
VIET_FONT_BOLD = 'TimesNewRomanVNBold'
VIET_FONT_ITALIC = 'TimesNewRomanVNItalic'


def register_vietnamese_fonts():
    """Đăng ký font tiếng Việt một lần duy nhất."""
    try:
        # Chỉ đăng ký nếu chưa có trong danh sách
        if VIET_FONT not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(VIET_FONT, 'C:/Windows/Fonts/times.ttf'))
            pdfmetrics.registerFont(TTFont(VIET_FONT_BOLD, 'C:/Windows/Fonts/timesbd.ttf'))
            pdfmetrics.registerFont(TTFont(VIET_FONT_ITALIC, 'C:/Windows/Fonts/timesi.ttf'))
    except Exception as e:
        print(f"!!! CẢNH BÁO: Lỗi đăng ký font: {e}")
        # Fallback nếu lỗi (để không crash app)
        return 'Times-Roman', 'Times-Bold', 'Times-Italic'

    return VIET_FONT, VIET_FONT_BOLD, VIET_FONT_ITALIC


def open_pdf_file(pdf_path):
    """Mở file PDF bằng trình xem mặc định của hệ điều hành."""
    try:
        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            os.system(f'open "{pdf_path}"')
        else:
            os.system(f'xdg-open "{pdf_path}"')
    except Exception as e:
        print(f"❌ Lỗi mở file: {e}")


def sanitize_filename(text):
    """Làm sạch chuỗi để dùng làm tên file."""
    if not text:
        return "unknown"
    return text.replace('/', '_').replace(':', '_').replace(' ', '__')


def get_paragraph_style(font_name, font_size, leading=None):
    """Tạo Style cho Paragraph nhanh chóng."""
    if leading is None:
        leading = font_size + 3
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        name=f'Style_{font_name}_{font_size}',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=font_size,
        leading=leading,
        alignment=TA_LEFT
    )