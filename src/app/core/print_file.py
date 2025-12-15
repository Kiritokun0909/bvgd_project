import subprocess
import sys

from app.utils.get_file_path import get_file_path
sumatra_path = r'C:\Users\hoduc\PycharmProjects\BVGD_Project\dist\SumatraPDF\SumatraPDF.exe'

if getattr(sys, 'frozen', False):
    sumatra_path = get_file_path("SumatraPDF/SumatraPDF.exe")

def print_file_win32(file_path):
    args = [
        sumatra_path,
        "-print-to-default",
        "-silent",
        "-exit-on-print",
        file_path
    ]
    try:
        # Gọi subprocess
        subprocess.run(args, check=True)
        # print("Đã gửi lệnh in đến máy in mặc định thành công.")
    except subprocess.CalledProcessError as e:
        print(f"Có lỗi xảy ra khi gọi SumatraPDF: {e}")