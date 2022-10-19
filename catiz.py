import sys

from ui_catiz import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from owslib.wms import WebMapService
from math import *
from shapely.geometry import box
from geopy import distance


def size_of_box(bbox):
    polygon = box(*bbox)
    print(polygon.area)


class Catiz(QtWidgets.QMainWindow):
    def __init__(self):
        super(Catiz, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.geoserver_url = 'http://localhost:8080/geoserver/wms'
        self.layer_name = 'catiz:gis_osm_places_a_free_1'
        self.map_output_size = (self.ui.tacsit.size().width(), self.ui.tacsit.size().height())
        self.wms = WebMapService(self.geoserver_url, version='1.1.1')
        self.zoom_level = 1
        self.current_bounding_box = self.wms.contents[self.layer_name].boundingBoxWGS84
        self.ui.zoom_in.clicked.connect(self.change_zoom)

        self.update_map()

    def update_map(self):
        img = self.wms.getmap( layers=['catiz:gis_osm_places_a_free_1'],
                          srs="EPSG:4326",
                          bbox=self.current_bounding_box,
                          size=self.map_output_size,
                          format='image/jpeg',
                          transparent=True)
        print(self._get_center())

        size_of_box(self.current_bounding_box)
        image_name = "caca.jpg"
        with open(image_name, 'wb') as temp_map_file:
            temp_map_file.write(img.read())

        self.ui.tacsit.setPixmap(QPixmap(image_name))

    def change_zoom(self):
        w, s, e, n = self.current_bounding_box
        dist = distance.distance((w,s), (e,n))
        self.zoom_level += 1
        target_dist = self.
        self.update_map()


    def _get_center(self):
        w, s, e, n = self.current_bounding_box
        width = max(w,e) - min(w,e)
        height = max(s,n) - min(s,n)
        center = round(min(s,n) +height/2, 4), round(min(w,e)+width/2,4)
        return center


app = QtWidgets.QApplication([])
application = Catiz()
application.show()
sys.exit(app.exec())