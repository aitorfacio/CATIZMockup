import sys

from mpl_toolkits.basemap import Basemap

from ui_catiz import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QObject, QTimer
from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from PyQt5.QtGui import QPixmap
from math import *
import numpy as np
from geopy import distance, Point
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import image
from matplotlib import animation
import matplotlib.pyplot as plt
from pathlib import Path
import pickle
from messaging import Client, random_name

def size_of_box(bbox):
    polygon = box(*bbox)
    print(polygon.area)


class MyCanvas(FigureCanvas):

    def __init__(self, *args, **kwargs):
        self.figure = plt.figure()
        FigureCanvas.__init__(self, self.figure)
        self.figure.patch.set_facecolor("None")
        self.figure.subplots_adjust(left=0.019, bottom=0.035, right=0.99, top=0.964)

class Catiz(QtWidgets.QMainWindow):
    def __init__(self):
        super(Catiz, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
#        self.map_output_size = (self.ui.tacsit.size().width(), self.ui.tacsit.size().height())
        self.zoom_level = 1
        self.current_bounding_box = None
        self.ui.zoom_in.clicked.connect(self.zoom_in)
        self.ui.zoom_out.clicked.connect(self.zoom_out)
        self.ui.set_center.clicked.connect(self.set_center)
        self.graph1 = MyCanvas()
        self.ui.gridLayout.addWidget(self.graph1, 0, 0, 1, 1)
        self.center = None
        self.axes = None
        self.axes_distance_x = 0
        self.axes_distance_y = 0
        self.pickle_filename = "caca.pickle"
        self.roles = ['CO','TAO','CSC', 'AAWC', 'ACS', 'HCM1', 'HCM2', 'SAMSC', 'GFCSC2', 'ASUWC',
                      'GFCSC1','SSMSC', 'ASWC', 'TLSC', 'ASAC','ATACO','TIC', 'EWS', 'IDS', '3DSRC', 'TNGS']
        self.mqtt_client = Client('172.21.144.106',id=random_name(20))
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.subscribe_list(['role/assign', 'role/unassign',
                                         'view/zoom', 'view/center',
                                         'view/video_radar/show'])
        self.mqtt_client.start()
        if Path(self.pickle_filename).exists():
            with open(self.pickle_filename, 'rb') as pickled_basemap:
                self.map = pickle.load(pickled_basemap)
        else:
            self.map = Basemap(resolution='l', projection='ortho', lat_0=0, lon_0=0)
            with open(self.pickle_filename, 'wb') as pickled_basemap:
                pickle.dump(self.map, pickled_basemap)

        for x in self.roles:
            child = QTreeWidgetItem(self.ui.roles)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setText(0, x)
            child.setCheckState(0, Qt.Unchecked)

        self.animation_point = None
        self.radar_timer = None
        self.radar_animation_offset = 0
        self.radar_points = None
        self.radar_type = None
        self.update_map()

    def on_message(self, client, userdata, message):
        if message.topic == "role/assign":
            self.role_assign(message.payload.decode('utf-8'), assign=True)
        elif message.topic == "role/unassign":
            self.role_assign(message.payload.decode('utf-8'), assign=False)
        elif message.topic == 'view/zoom':
            self.zoom_configure(message.payload.decode('utf-8'))
        elif message.topic == 'view/center':
            self.show_handler_not_implemented(message.topic)
        elif message.topic == 'view/video_radar/show':
            self.show_handler_not_implemented(message.topic)
        elif message.topic == 'view/video_radar/hide':
            self.show_handler_not_implemented(message.topic)
            #self.show_radar(message.payload.decode('utf-8'))

    def show_handler_not_implemented(self, topic_id):
        QMessageBox.about(self, "Not implemented", f"The handler for {topic_id} is not implemented.").exec()

    def timer_started(self):
        print("Timer started")

    def show_radar(self, type_of_radar=None):
        if not self.radar_type:
            self.radar_type = type_of_radar
        #file_path = 'gaviota.jpg'
        #img = image.imread(file_path)
        if self.radar_points:
            self.radar_points.remove()

        lats = list(range(100))
        lons = list(range(100))
        lats = [x + self.radar_animation_offset for x in lats]
        lons = [x + self.radar_animation_offset for x in lons]
        self.radar_animation_offset += 1
        x, y = self.map(lons, lats)
        self.radar_points = self.map.scatter(x, y, marker='o')
        self.graph1.figure.canvas.draw()
        if not self.radar_timer:
            self.radar_timer = QTimer(self)
            self.radar_timer.timeout.connect(self.show_radar)
            self.radar_timer.start(100)

        #if not self.animation_point:
        #    x, y = self.map(0,0)
        #    self.animation_point = self.map.plot(x, y, 'ro')[0]
        #def init():
        #    self.animation_point.set_data([],[])
        #    return self.animation_point,
        #def animate(i):
        #    lons, lats = np.random.random_integers(-130,130, 2)
        #    x, y = self.map(lons, lats)
        #    self.animation_point.set_data(x,y)
        #    return self.animation_point,
        #anim = animation.FuncAnimation(self.graph1.figure, animate, init_func=init, frames=20, interval=500, blit=True)
        #self.graph1.draw()


    def role_assign(self, role, assign=True):
        clist = self.ui.roles.findItems(role, Qt.MatchExactly | Qt.MatchRecursive,0)
        if clist:
            item = clist[0]
            state = assign and Qt.Checked or Qt.Unchecked
            item.setCheckState(0, state)
            self.ui.roles.viewport().update()

    def zoom_configure(self, zoom_level):
        zoom_level = int(zoom_level)
        if zoom_level == -1:
            self.zoom_out()
        elif zoom_level == 0:
            self.zoom_in()
        else:
            zoom_exponent = int(log(zoom_level, 2))
            zoom_offset = abs(self.zoom_level - zoom_exponent)
            if zoom_exponent> self.zoom_level:
                for i in range(zoom_offset -1):
                    self.zoom_in(redraw=False)
                self.zoom_in()
            elif zoom_exponent < self.zoom_level:
                for i in range(zoom_offset -1):
                    self.zoom_out(redraw=False)
                self.zoom_out()

    def zoom(self, amount):
        xmin, xmax = self.axes.get_xbound()
        ymin, ymax = self.axes.get_ybound()
        centerx = (xmax + xmin) / 2
        centery = (ymax + ymin) / 2
        offset_x = self.axes_distance_x / self.zoom_level
        offset_y = self.axes_distance_y / self.zoom_level
        #self.axes.set_xbound(self.axes.get_xbound()[0] * (1.0 / amount), self.axes.get_xbound()[1] * amount)
        #self.axes.set_ybound(self.axes.get_ybound()[0] * (1.0 / amount), self.axes.get_ybound()[1] * amount)
        self.axes.set_xbound(centerx - offset_x, centerx + offset_x)
        self.axes.set_ybound(centery - offset_y, centery + offset_y)

    def update_map(self):
        self.graph1.figure.clf()
        if not self.axes:
            self.axes = self.graph1.figure.add_subplot(111)
        if not self.current_bounding_box:
            self.current_bounding_box = (self.map.llcrnrlat, self.map.llcrnrlon,
                                         self.map.urcrnrlat, self.map.urcrnrlon)
        self.map.drawmapboundary(fill_color='#00BFFF', zorder=1)
        self.map.fillcontinents(color='#F5D0A9', zorder=2, lake_color='aqua')
        self.map.bluemarble()
        if not self.center:
            self.set_center()
        lat, lon = self.center.latitude, self.center.longitude
        self.map.plot(lon, lat, "o", latlon=True)
        xmin, xmax = self.axes.get_xbound()
        ymin, ymax = self.axes.get_ybound()
        self.axes_distance_x = xmax - xmin
        self.axes_distance_y = ymax - ymin


    def zoom_in(self, redraw=True):
        self.zoom_level += 1
        if self.zoom_level > 12:
            self.zoom_level = 12
        else:
        ##target_dist = self.
        #xmin, xmax = self.axes.get_xlim()
        #ymin, ymax = self.axes.get_ylim()
        #self.axes.set_xlim([xmin/2, xmax/2])
        #self.axes.set_ylim([ymin/2, ymax/2])
            self.zoom(self.zoom_level*0.5/12)
            if redraw:
                self.graph1.draw()

    def zoom_out(self, redraw=True):
        self.zoom_level -= 1
        if self.zoom_level < 1:
            self.zoom_level = 1
        else:
            self.zoom(12 - self.zoom_level)
            if redraw:
                self.graph1.draw()

    def set_center(self):
        self.center = Point(latitude=self.map.projparams['lat_0'], longitude=self.map.projparams['lon_0'])


app = QtWidgets.QApplication([])
application = Catiz()
application.show()
sys.exit(app.exec())