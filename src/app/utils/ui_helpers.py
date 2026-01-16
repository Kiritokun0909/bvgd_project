import abc
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QEvent

from app.configs.table_thuoc_configs import COL_MA_THUOC
from app.services.DichVuService import get_list_dich_vu_by_keyword
from app.services.DoiTuongService import get_doi_tuong_by_keyword
from app.services.ICDService import get_list_icd
from app.services.DuocService import get_list_duoc
from app.styles.styles import COMPLETER_THUOC_STYLE

class BaseCompleterHandler(QtCore.QObject):
    activated_with_data = QtCore.pyqtSignal(str, object)

    def __init__(self, parent=None, min_search_length: int = 2, popup_min_width: int = None):
        super().__init__(parent)
        self.model = QtCore.QStringListModel(self)
        self.completer = QtWidgets.QCompleter(self.model, self)
        self.timer = QtCore.QTimer(self)

        self.min_search_length = min_search_length

        self.completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        popup_view = self.completer.popup()
        popup_view.setStyleSheet(COMPLETER_THUOC_STYLE)

        if popup_min_width is not None and popup_min_width > 0:
            popup_view.setMinimumWidth(popup_min_width)

        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._perform_search)

        self._current_text = ""
        self._raw_data_cache = []
        self._line_edit = None

    def connect_to(self, line_edit: QtWidgets.QLineEdit):
        self._line_edit = line_edit

        popup_view = self.completer.popup()
        if popup_view.minimumWidth() == 0:
            popup_view.setMinimumWidth(line_edit.width())

        line_edit.setCompleter(self.completer)
        line_edit.textEdited.connect(self.start_search)

        if self.min_search_length == 0:
            line_edit.installEventFilter(self)

        try:
            self.completer.activated.disconnect()
        except TypeError:
            pass
        self.completer.activated.connect(self._on_item_activated)

    def eventFilter(self, source, event):
        """Bắt sự kiện Focus để tự động tìm kiếm nếu min_search_length = 0"""
        if source is self._line_edit and event.type() == QEvent.Type.FocusIn:
            if self.min_search_length == 0:
                # Kích hoạt tìm kiếm ngay lập tức với text hiện tại (kể cả rỗng)
                self.start_search(self._line_edit.text())
        return super().eventFilter(source, event)

    def start_search(self, text: str):
        self._current_text = text.strip()
        search_len = len(self._current_text)
        self.timer.stop()

        if search_len < self.min_search_length:
            self.model.setStringList([])
            self.completer.popup().hide()
            return

        self.timer.start(200)

    @abc.abstractmethod
    def _fetch_and_format_data(self, keyword: str) -> list:
        raise NotImplementedError

    def _perform_search(self):
        keyword = self._current_text
        if len(keyword) < self.min_search_length and self.min_search_length > 0:
            return

        try:
            results = self._fetch_and_format_data(keyword)
            display_list = [item[0] for item in results]
            self._raw_data_cache = results

            self.model.setStringList(display_list[:])

            if self.model.rowCount() > 0 and self._line_edit and self._line_edit.hasFocus():
                self.completer.complete()
            else:
                self.completer.popup().hide()
        except Exception as e:
            print(f"Lỗi khi tìm kiếm (handler): {e}")
            self.model.setStringList([])

    def _on_item_activated(self, selected_text: str):
        for display, raw in self._raw_data_cache:
            if display == selected_text:
                self.activated_with_data.emit(selected_text, raw)
                return
        self.activated_with_data.emit(selected_text, None)


# --- Lớp con cho DoiTuong ---

class DoiTuongCompleterHandler(BaseCompleterHandler):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)

    def _fetch_and_format_data(self, keyword: str) -> list:
        raw_data_list = get_doi_tuong_by_keyword(keyword=keyword)
        results = []
        for raw_item in raw_data_list:
            if len(raw_item) >= 1:
                display_string = f"{raw_item[1]}"
                results.append((display_string, raw_item))
        return results


# --- Lớp con cho ICD ---

class IcdCompleterHandler(BaseCompleterHandler):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)

    def _fetch_and_format_data(self, keyword: str) -> list:
        raw_data_list = get_list_icd(keyword=keyword)
        results = []
        for raw_item in raw_data_list:
            if len(raw_item) >= 1:
                display_string = f"{raw_item[0]} - {raw_item[1]}"  # <-- ĐÃ SỬA
                results.append((display_string, raw_item))
        return results


# --- Lớp con cho Dược ---

class DuocCompleterHandler(BaseCompleterHandler):

    # 1. Cập nhật __init__ để nhận table_widget
    def __init__(self, table_widget: QtWidgets.QTableWidget, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.table_widget = table_widget
        self.doi_tuong_id = None

    def set_ma_doi_tuong(self, ma_doi_tuong: str):
        self.doi_tuong_id = ma_doi_tuong

    # 2. Thêm hàm helper để đọc bảng
    def _get_added_drug_ids(self) -> set:
        """Lấy set các MaDuoc đã có trong bảng (trừ dòng nhập liệu)."""
        added_ids = set()
        for row in range(1, self.table_widget.rowCount()):
            item = self.table_widget.item(row, COL_MA_THUOC)
            if item and item.text():
                added_ids.add(item.text().strip())
        return added_ids

    # 3. Cập nhật _fetch_and_format_data để lọc
    def _fetch_and_format_data(self, keyword: str) -> list:
        if not keyword and self.min_search_length > 0:
            return []

        # Lấy danh sách ID đã thêm vào bảng
        added_ids = self._get_added_drug_ids()

        # Gọi service
        raw_data_list = get_list_duoc(keyword, self.doi_tuong_id)

        results = []
        for raw_item in raw_data_list:
            # raw_item: (Duoc_Id, MaDuoc, TenDuocDayDu, ...)
            if len(raw_item) >= 3:
                ma_duoc = raw_item[1]

                # *** LOGIC LỌC MỚI: Chỉ thêm nếu chưa có trong bảng ***
                if ma_duoc not in added_ids:
                    ten_duoc = raw_item[2]
                    display_string = f"{ten_duoc} ({ma_duoc})"
                    results.append((display_string, raw_item))

        return results


# --- Lớp con cho Dịch vụ ---

class DichVuCompleterHandler(BaseCompleterHandler):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.doi_tuong_id = None

    def set_ma_doi_tuong(self, ma_doi_tuong: str):
        self.doi_tuong_id = ma_doi_tuong

    def _fetch_and_format_data(self, keyword: str) -> list:
        if (not keyword and self.min_search_length > 0) or not self.doi_tuong_id:
            return []

        raw_data_list = get_list_dich_vu_by_keyword(self.doi_tuong_id, keyword)

        if not raw_data_list:
            return []

        results = []
        for raw_item in raw_data_list:
            # (DICH_VU_ID, INPUT_CODE, TEN_DICH_VU, TEN_KHONG_DAU)
            if len(raw_item) >= 3:
                input_code = raw_item[1]
                ten_dv = raw_item[2]
                display_string = f"{ten_dv} ({input_code})"
                results.append((display_string, raw_item))
        return results


