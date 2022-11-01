import sys

from mpl_toolkits.basemap import Basemap
from numpy import meshgrid

from generic_window import GenericWindow
from ui_catiz import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QObject, QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox, QMenu, QCheckBox
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
import matplotlib.pyplot as plt
from pathlib import Path
import pickle
from messaging import Client, random_name
from functools import partial

def size_of_box(bbox):
    polygon = box(*bbox)
    print(polygon.area)

class Track(object):
    def __init__(self, id, lat, lon):
        self.id = id
        self.lat = lat
        self.lon = lon





class MyCanvas(FigureCanvas):

    def __init__(self, *args, **kwargs):
        self.figure = plt.figure()
        FigureCanvas.__init__(self, self.figure)
        self.figure.patch.set_facecolor("None")
        self.figure.subplots_adjust(left=0.019, bottom=0.035, right=0.99, top=0.964)

class Catiz(QtWidgets.QMainWindow):
    show_info = pyqtSignal(str, str)
    open_window_received = pyqtSignal(str)
    mute_equipment_received = pyqtSignal(str, bool)
    add_alert_received = pyqtSignal(str)
    review_alerts_received = pyqtSignal()
    create_track_received = pyqtSignal(float, float)

    def __init__(self):
        super(Catiz, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
#        self.map_output_size = (self.ui.tacsit.size().width(), self.ui.tacsit.size().height())
        self.zoom_level = 1
        self.current_bounding_box = None
        self.ui.zoom_in.clicked.connect(self.zoom_in)
        self.ui.zoom_out.clicked.connect(self.zoom_out)
        self.training_mode = False
        self.graph1 = MyCanvas()
        self.ui.gridLayout.addWidget(self.graph1, 0, 0, 1, 1)
        self.center = None
        self.axes = None
        self.axes_distance_x = 0
        self.axes_distance_y = 0
        self.pickle_filename = "caca.pickle"
        self.roles = ['CO','TAO','CSC', 'AAWC', 'ACS', 'HCM1', 'HCM2', 'SAMSC', 'GFCSC2', 'ASUWC',
                      'GFCSC1','SSMSC', 'ASWC', 'TLSC', 'ASAC','ATACO','TIC', 'EWS', 'IDS', '3DSRC', 'TNGS']
        self.windows = ['AIS_CONTACT_LIST','TACTICAL_TRACK_SUMMARY','TRACK_ID_SUMMARY','TRACK_LIST','ENGAGEMENT_STATUS',
                        'FORCE_WEAPON_INVENTORY','JRE_CHAT','TEXT_MESSAGE','TACTICAL_DOCTRINE_TRACK_LIST',
                        'CONSOLE_STATUS','DATA_RECORDING_CONTROL','NAVIGATION_SUPPORT_LIST','NAVIGATION_RECCOMENDATIONS',
                        'TRIAL_MANEUVER','MANEUVER_CONTROL','TACTICAL_DECISION_AIDS','CPA','AIS_DATA_FILTER',
                        'COMPASS_ROSE','GEO','GRIDS','CLOSE_CONTROL_FILTER','OVERLAYS','SPECIAL_POINTS','IFF_DATA',
                        'GFCS_DISPLAY','LSD_CONFIGURATION','EW','SAM','SSM','EOSS','3DR','DLS','UAS','TLS']
        self.equipment = {x: False for x in ['GFCSC1', 'GFCSC2', 'R3D', 'CDL', 'EWR', 'EWC', 'IFF', 'TAS']}
        self.tracks = []
        self.track_file = 'tracks_caca.txt'
        self.track_figures = None
        self.next_track_id = 8001
        self.mqtt_client = Client('172.21.144.106', id=random_name(20))
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.subscribe_list(['role/assign', 'role/unassign',
                                         'view/zoom', 'view/center',
                                         'view/video_radar/show', 'view/video_radar/hide',
                                         'view/window/open', 'training/enter',
                                         'training/exit', 'equipment/mute', 'equipment/unmute',
                                         'alerts/review', 'tracks/info', 'tracks/engaged',
                                         'tracks/break_engagement', 'tracks/list',
                                         ##interal use topics
                                         'alerts/new', 'tracks/create', 'tracks/delete'
                                         ])
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
        self.show_info.connect(self.show_message)
        #for w in self.windows[:5]:
        #    self.ui.menubar.addMenu(w)

        #k, m = divmod(len(self.windows), 5)
        n = 5
#        window_groups = list(self.windows[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(len(self.windows)))
        window_groups = [self.windows[i*n:(i+1)*n] for i in range((len(self.windows) + n - 1) // n)]
        for index, wg in enumerate(window_groups):
            menu = self.ui.menubar.addMenu(f"Window Group {index}")
            self.ui.menubar.setStyleSheet('QMenuBar{color: #ffff00;}')
            menu.setStyleSheet('QMenu{color: #ffff00;}')
            for w in wg:
                act = menu.addAction(w)
                act.triggered.connect(partial(self.open_window, w))

        self.selected_window = None
        self.open_window_received.connect(self.open_window)
        self.set_training_mode(self.training_mode)
        row = 0
        col = 0
        row_size = 5
        for eq, status in self.equipment.items():
            chk = QCheckBox(self)
            chk.setObjectName(eq)
            chk.setText(eq)
            chk.setStyleSheet('QCheckBox{ color: #ffff00;}')
            self.ui.equipment_status.addWidget(chk, row, col)
            self.set_equipment_status(eq, status)
            col += 1
            if col >= row_size:
                col = 0
                row += 1
        self.mute_equipment_received.connect(self.set_equipment_status)
        self.add_alert_received.connect(self.add_alert)
        self.review_alerts_received.connect(self.clear_alerts)
        self.create_track_received.connect(self.create_track)
        self.ui.roles.setStyleSheet('QHeaderView::section{ background-color:00004b;}\n'
                                    'QTreeWidget{color:#ffff00;}')

        self.update_map()
        with open(self.track_file, 'r') as track_f:
            track_list = track_f.readlines()
            track_id_index = 8001
            for t in track_list:
                lat, lon = t.split()
                lat, lon = float(lat), float(lon)
                my_track = Track(str(track_id_index), lat, lon)
                self.tracks.append(my_track)
                track_id_index += 1
        lats = [t.lat for t in self.tracks]
        lons = [t.lon for t in self.tracks]
        x, y = self.map(lons, lats)
        self.map.scatter(x, y)


    @pyqtSlot()
    def clear_alerts(self):
        self.ui.alerts.clear()

    @pyqtSlot(str)
    def add_alert(self, alert_text):
        self.ui.alerts.insertPlainText(f'{alert_text}\n')

    @pyqtSlot(float, float)
    def create_track(self, lat, lon):
        print(f"create_track({lat}, {lon}) called")
        t = Track(self.next_track_id, lat, lon)
        print(f"created_track with id {t.id}")
        self.next_track_id += 1
        self.tracks.append(t)

        x, y = self.map([t.lon for t in self.tracks],[t.lat for t in self.tracks])
        self.map.scatter(x, y, zorder=10)
        #for t in self.tracks:
        #    tx, ty = self.map(t.lon, t.lat)
        #    plt.text( tx-20, ty-20, str(t.id),zorder=10)

    def set_training_mode(self, active):
        training_text = active and "Active" or "Inactive"
        self.training_mode = active
        self.ui.tranining_mode.setText(training_text)

    @pyqtSlot(str)
    def open_window(self, window_name):
        self.selected_window = GenericWindow(self, window_name)
        self.selected_window.open()

    @pyqtSlot(str, bool)
    def set_equipment_status(self, name, muted):
        if muted:
            status = Qt.Unchecked
        else:
            status = Qt.Checked
        chkbox = None
        for i in range(self.ui.equipment_status.count()):
            c = self.ui.equipment_status.itemAt(i)
            if c.widget().objectName() == name:
                chkbox = c.widget()
                break
        if chkbox:
            self.equipment[name] = muted
            chkbox.setCheckState(status)

    def on_message(self, client, userdata, message):
        print(f"Received {message.topic}")
        if message.topic == "role/assign":
            self.role_assign(message.payload.decode('utf-8'), assign=True)
        elif message.topic == "role/unassign":
            self.role_assign(message.payload.decode('utf-8'), assign=False)
        elif message.topic == 'view/zoom':
            self.zoom_configure(message.payload.decode('utf-8'))
        elif message.topic == 'view/window/open':
            self.open_window_received.emit(message.payload.decode('utf-8'))
        elif message.topic == 'training/enter':
            self.set_training_mode(True)
        elif message.topic == 'training/exit':
            self.set_training_mode(False)
        elif message.topic == 'equipment/mute':
            self.mute_equipment_received.emit(message.payload.decode('utf-8'), True)
        elif message.topic == 'equipment/unmute':
            self.mute_equipment_received.emit(message.payload.decode('utf-8'), False)
        elif message.topic == 'alerts/new':
            self.add_alert_received.emit(message.payload.decode('utf-8'))
        elif message.topic == 'alerts/review':
            self.review_alerts_received.emit()
        elif message.topic == 'tracks/create':
            lat, lon = message.payload.decode('utf-8').split('_')
            lat, lon = float(lat), float(lon)
            self.create_track_received.emit(lat, lon)


        #elif message.topic == 'view/center':
        #    self.show_handler_not_implemented(message.topic)
        #elif message.topic == 'view/video_radar/show':
        #    self.show_handler_not_implemented(message.topic)
        #elif message.topic == 'view/video_radar/hide':
        #    self.show_handler_not_implemented(message.topic)
        else:
            self.show_handler_not_implemented(message.topic)

    #self.show_radar(message.payload.decode('utf-8'))

    def show_handler_not_implemented(self, topicid):
        self.show_info.emit("Not Implemented", f"The handler for {topicid} is not implemented.")

    @pyqtSlot(str, str)
    def show_message(self, title, message):
        QMessageBox.about(self, title, message)
        #QMessageBox.about(self, "Not implemented", f"The handler for {topic_id} is not implemented.").exec()

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