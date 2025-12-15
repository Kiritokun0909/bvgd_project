from PyQt6.QtCore import QSettings

# Định nghĩa các khóa (Keys) sẽ được lưu trong QSettings
KEY_PHONG_KHAM = "user/last_phong_kham"
KEY_TEN_BAC_SI = "user/last_ten_bac_si"
KEY_TAI_VU_NGUOI_TAO = "tai_vu/nguoi_tao"
KEY_TAI_VU_NGUOI_THU = "tai_vu/nguoi_thu"

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

    def load_last_selection(self) -> tuple:
        """Tải mã phòng khám và tên bác sĩ đã lưu."""

        # Tải giá trị. Tham số thứ hai là giá trị mặc định nếu không tìm thấy.
        phong_kham = self.settings.value(KEY_PHONG_KHAM, "")
        bac_si = self.settings.value(KEY_TEN_BAC_SI, "")

        return str(phong_kham), str(bac_si)

    def save_last_tai_vu_selection(self, ten_nguoi_tao: str, ten_nguoi_thu: str):
        """Lưu lại tên người tạo và tên người thu ở màn hình Tài vụ."""
        self.settings.setValue(KEY_TAI_VU_NGUOI_TAO, ten_nguoi_tao)
        self.settings.setValue(KEY_TAI_VU_NGUOI_THU, ten_nguoi_thu)
        self.settings.sync()

    def load_last_tai_vu_selection(self) -> tuple:
        """Tải tên người tạo và tên người thu đã lưu."""
        nguoi_tao = self.settings.value(KEY_TAI_VU_NGUOI_TAO, "")
        nguoi_thu = self.settings.value(KEY_TAI_VU_NGUOI_THU, "")

        return str(nguoi_tao), str(nguoi_thu)

