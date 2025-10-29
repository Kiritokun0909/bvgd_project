from PyQt6.QtCore import QSettings

# Định nghĩa các khóa (Keys) sẽ được lưu trong QSettings
KEY_PHONG_KHAM = "user/last_phong_kham"
KEY_TEN_BAC_SI = "user/last_ten_bac_si"

# Tên công ty/ứng dụng để QSettings biết nên lưu dữ liệu vào đâu
APP_ORG = "BVGD_Project"
APP_NAME = "KhamBenhApp"


class ConfigManager:
    """
    Quản lý việc lưu và tải các cài đặt nhỏ của người dùng
    dùng QSettings.
    """

    def __init__(self):
        # QSettings sử dụng QSettings.IniFormat nếu không được đặt
        self.settings = QSettings(APP_ORG, APP_NAME)

    def save_last_selection(self, phong_kham_code: str, ten_bac_si: str):
        """Lưu lại mã phòng khám và tên bác sĩ cuối cùng đã chọn."""

        # Lưu vào QSettings
        self.settings.setValue(KEY_PHONG_KHAM, phong_kham_code)
        self.settings.setValue(KEY_TEN_BAC_SI, ten_bac_si)

        # Ép buộc ghi dữ liệu ra đĩa ngay lập tức
        self.settings.sync()

    def load_last_selection(self) -> tuple[str, str]:
        """Tải mã phòng khám và tên bác sĩ đã lưu."""

        # Tải giá trị. Tham số thứ hai là giá trị mặc định nếu không tìm thấy.
        phong_kham = self.settings.value(KEY_PHONG_KHAM, "")
        bac_si = self.settings.value(KEY_TEN_BAC_SI, "")

        return str(phong_kham), str(bac_si)