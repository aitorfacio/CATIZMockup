from ui_track_info import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QStyle, QHeaderView


class TrackInfo(QDialog):
    def __init__(self, parent=None, track_list=None):
        super(TrackInfo, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.tableWidget.verticalHeader().setVisible(False)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.track_list = track_list
        for f in self.track_list:
            row_position = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row_position)
            self.ui.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(f.id)))
            self.ui.tableWidget.setItem(row_position, 1, QTableWidgetItem(str(f.lat)))
            self.ui.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(f.lon)))
            self.ui.tableWidget.setItem(row_position, 3, QTableWidgetItem(str(f.type)))
            self.ui.tableWidget.setItem(row_position, 4, QTableWidgetItem(f.engaged and "Engaged" or "Not Engaged"))
