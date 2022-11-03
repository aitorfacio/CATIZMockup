from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from ui_tracks_by_type import Ui_Dialog

class TracksByType(QDialog):
    def __init__(self, parent=None, tracks=None, types=None):
        super(TracksByType, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.tracks = tracks

        summary = {}
        for sensor in types:
            summary[sensor] = sum(t.type == sensor for t in self.tracks)

        for type in sorted(summary.keys()):
            row_index = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row_index)
            self.ui.tableWidget.setItem(row_index, 0, QTableWidgetItem(type))
            self.ui.tableWidget.setItem(row_index, 1, QTableWidgetItem(str(summary[type])))

