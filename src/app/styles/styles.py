# styles.py (Phiên bản Cải Tiến)

DELETE_BTN_STYLE = """
QPushButton {
    /* Mặc định: Đỏ cảnh báo */
    background-color: #dc3545; /* Màu Đỏ Sáng */
    color: white;
    font-size: 15px;
    font-weight: bold;
    border: 2px solid #bd2130; /* Viền đỏ đậm hơn */
    border-radius: 8px;
    padding: 5px 5px;
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2); /* Đổ bóng nhẹ */
}
QPushButton:hover {
    /* Khi di chuột: Đậm màu hơn */
    background-color: #c82333;
    border: 2px solid #8e1c26;
}
QPushButton:pressed {
    /* Khi nhấn: Tối màu hơn và tạo hiệu ứng "ấn xuống" */
    background-color: #a71d2a;
    box-shadow: none; /* Bỏ bóng để tạo cảm giác bị nhấn */
    padding-top: 12px;
    padding-bottom: 8px;
}
QPushButton:disabled {
    /* Khi bị vô hiệu hóa */
    background-color: #f0f0f0;
    color: #a9a9a9;
    border: 1px solid #d3d3d3;
}
"""

ADD_BTN_STYLE = """
QPushButton {
    /* Mặc định: Xanh dương hành động chính */
    background-color: #007bff; /* Màu Xanh Dương */
    color: white;
    font-size: 15px;
    font-weight: bold;
    border: 2px solid #0056b3;
    border-radius: 8px;
    padding: 5px 5px;
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
}
QPushButton:hover {
    /* Khi di chuột: Đậm màu hơn */
    background-color: #0069d9;
    border: 2px solid #004c99;
}
QPushButton:pressed {
    /* Khi nhấn: Tối màu hơn và tạo hiệu ứng "ấn xuống" */
    background-color: #004d9c;
    box-shadow: none;
    padding-top: 12px;
    padding-bottom: 8px;
}
QPushButton:disabled {
    /* Khi bị vô hiệu hóa */
    background-color: #f0f0f0;
    color: #a9a9a9;
    border: 1px solid #d3d3d3;
}
"""

TUOI_STYLE = """
    font-weight: 700; 
    font-size: 20px;
"""

COMPLETER_THUOC_STYLE = """
    QListView {
        /* Viền bao quanh cửa sổ popup */
        border: 1px solid #0078D4; 
        border-radius: 5px; 
        background-color: #ebebeb;
        font-size: 14px;
        selection-background-color: #ADD8E6; 
        selection-color: black;
        padding: 4px;
    }
    QListView::item {
        /* Tùy chỉnh mỗi mục trong danh sách gợi ý */
        padding: 4px;
        min-height: 25px; 
        font-size: 14px;
    }
    QListView::item:selected {
        /* Giao diện khi mục được chọn */
        background-color: #0078D4; 
        color: white;
        border: none; /* Đảm bảo loại bỏ viền focus */
        outline: none;
    }
"""

TAI_VU_STYLE = """
    font-weight: 700; 
    font-size: 14px;
"""