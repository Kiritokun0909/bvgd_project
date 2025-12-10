# import win32api
# import win32print
import os


def print_file_win32(file_path):
    """
    In tệp sử dụng API Windows (yêu cầu pywin32).
    """
    try:
        os.startfile(file_path, "print")

        # Lấy máy in mặc định
        # default_printer = win32print.GetDefaultPrinter()
        # print(default_printer)
        #
        # # Lệnh in. 'printto' là một động từ shell, nó sẽ gọi chương trình
        # # được liên kết với loại tệp để in (ví dụ: Acrobat Reader cho PDF)
        # win32api.ShellExecute(
        #     0,
        #     "printto",  # 'print' cho hộp thoại, 'printto' cho in trực tiếp
        #     file_path,
        #     default_printer,
        #     ".",
        #     0
        # )
        # print(f"Đã gửi '{file_path}' đến '{default_printer}' để in.")
    except Exception as e:
        print(f"Lỗi khi in bằng win32api: {e}")

# Ví dụ:
# print_file_win32("D:\\path\\to\\your\\report.docx")