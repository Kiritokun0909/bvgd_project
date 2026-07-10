Công cụ dựa trên Python này tự động hóa quy trình sao chép (mirror) thư mục phân phối cục bộ sang nhiều Máy ảo (VM) hoặc máy chủ từ xa qua mạng nội bộ. Nó bao gồm kiểm tra kết nối (Ping), nhắm mục tiêu theo nhóm và xử lý các chia sẻ mạng có yêu cầu xác thực.

## 📋 Tính năng
* **Danh sách mục tiêu từ Excel:** Đọc địa chỉ IP mục tiêu và tên nhóm từ tệp `IpAddress.xlsx`.
* **Lựa chọn theo nhóm:** Cho phép đồng bộ hóa với tất cả các máy hoặc các nhóm cụ thể (ví dụ: các phòng ban hoặc khoa cụ thể).
* **Nhận biết kết nối:** Bỏ qua các máy đang ngoại tuyến để tiết kiệm thời gian.
* **Tự động xác thực:** Xử lý các chia sẻ mạng được bảo vệ bằng mật khẩu bằng cách sử dụng `net use`.
* **Đồng bộ hóa mạnh mẽ:** Sử dụng `Robocopy /E` để đảm bảo đích đến được cập nhật với nội dung nguồn.
* **Ghi nhật ký chi tiết:** Tạo nhật ký riêng biệt có gắn dấu thời gian cho mọi máy.

Trước khi chạy tập lệnh, bạn **phải** cập nhật các biến cấu hình trong `sync.py` để phù hợp với môi trường cục bộ của bạn.

1.  **Mở `src/tools/sync_app/sync.py` trong trình chỉnh sửa văn bản.**
2.  **Tìm phần `--- CONFIGURATION ---` ở trên cùng.**
3.  **Cập nhật các biến sau:**

    *   `EXCEL_PATH`: Đường dẫn tuyệt đối đến tệp `IpAddress.xlsx` của bạn.
        *   *Tệp Excel phải có các cột: `GroupName` và `IpAddress`.*
    *   `LOCAL_FOLDER`: Đường dẫn tuyệt đối của **thư mục nguồn** bạn muốn sao chép (ví dụ: đầu ra bản build hoặc thư mục phân phối).
    *   `REMOTE_SHARE`: Tên chia sẻ hoặc đường dẫn trên các máy ảo đích.
    *   `LOG_FOLDER`: Thư mục nơi các nhật ký thực thi sẽ được lưu lại.
    *   `USERNAME`: Tên đăng nhập để xác thực chia sẻ mạng.
    *   `PASSWORD`: Mật khẩu để xác thực chia sẻ mạng.

## 📦 Yêu cầu hệ thống

* Python 3.x
* Thư viện `pandas` và `openpyxl`:
  ```bash
  pip install pandas openpyxl
  ```

## 🚀 Cách sử dụng

### Chạy thủ công
1. Mở terminal hoặc PowerShell.
2. Di chuyển đến thư mục gốc của dự án.
3. Thực thi tập lệnh:
   ```bash
   python src/tools/sync_app/sync.py
   ```
4. **Chọn mục tiêu:** Khi được hỏi, nhập `All` để đồng bộ toàn bộ hoặc nhập một `GroupName` cụ thể (ví dụ: `KHAMBENH`).

### 📅 Lập lịch (Mỗi Chủ Nhật)

Để tự động hóa tác vụ này cho mạng bệnh viện, hãy thiết lập nó trong
Windows Task Scheduler **(taskschd.msc)**:

1. **Tạo tác vụ (Create Task)**

    Mở **Task Scheduler** và nhấp vào **Create Basic Task**.

    * Tên (Name): Weekly_App_Sync

    * Trình kích hoạt (Trigger): Chọn Weekly (Hàng tuần).

    * Ngày (Day): Chọn Chủ Nhật.

    * Thời gian (Time): Đặt vào thời điểm ít lưu lượng truy cập (ví dụ: 02:00 AM).


2. **Cấu hình hành động (Configure the Action)**

    * Hành động (Action): Start a program (Chạy một chương trình).

    * Chương trình/tập lệnh (Program/script): **ĐƯỜNG_DẪN_ĐẾN_PYTHON_EXE_CỦA_BẠN**, ví dụ:  
    ```
        C:\Users\{TÊN_NGƯỜI_DÙNG}\PycharmProjects\{TÊN_DỰ_ÁN}\.venv\Scripts\python.exe
    ```

    * Thêm đối số (Add arguments): **ĐƯỜNG_DẪN_ĐẾN_TẬP_LỆNH_PYTHON_CỦA_BẠN**, ví dụ:
    ```
        C:\Users\{TÊN_NGƯỜI_DÙNG}\PycharmProjects\{TÊN_DỰ_ÁN}\src\tools\sync_app\sync.py
    ```
   
    * Tham khảo: https://community.esri.com/t5/python-documents/schedule-a-python-script-using-windows-task/ta-p/915861
