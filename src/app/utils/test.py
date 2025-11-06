from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A5

import tempfile
import sys
import os

def hello(c):
    # move the origin up and to the left
    c.translate(inch,inch)
    # define a large font
    c.setFont("Helvetica", 14)
    # choose some colors
    c.setStrokeColorRGB(0.2,0.5,0.3)
    c.setFillColorRGB(1,0,1)
    # draw some lines
    c.line(0,0,0,1.7*inch)
    c.line(0,0,1*inch,0)
    # draw a rectangle
    c.rect(0.2*inch,0.2*inch,1*inch,1.5*inch, fill=1)
    # make text go straight up
    # c.rotate(90)
    # change color
    c.setFillColorRGB(0,0,0.77)
    # say hello (note after rotate the y coord needs to be negative!)
    c.drawString(0.3*inch, inch, "Hello World")

def create_and_open_pdf_for_printing():
    """Tạo file PDF tạm thời bằng ReportLab và mở file."""
    try:
        # 1. Tạo tệp PDF tạm thời
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name

        # 2. Khởi tạo canvas với kích thước A4 (hoặc kích thước tùy chỉnh)
        c = canvas.Canvas(pdf_path, pagesize=A5)

        # 4. Gọi hàm vẽ nội dung phiếu
        hello(c)

        # Kết thúc và lưu file PDF
        c.showPage()
        c.save()

        print(f"Đã tạo file PDF tạm tại: {pdf_path}")

        # 5. Mở file PDF để in
        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            os.system(f'open "{pdf_path}"')
        else:
            os.system(f'xdg-open "{pdf_path}"')

    except Exception as e:
        print(f"Đã xảy ra lỗi khi tạo PDF với ReportLab: {e}")

if __name__ == "__main__":
    create_and_open_pdf_for_printing()
