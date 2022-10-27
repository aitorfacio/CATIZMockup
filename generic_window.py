from ui_generic_window import Ui_Dialog
from PyQt5.QtWidgets import QDialog

class GenericWindow(QDialog):
    def __init__(self, parent=None, window_type=None):
        super(GenericWindow, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.window_name = window_type
        self.ui.window_name.setText(self.window_name)