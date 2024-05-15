import sys
import configparser
import time

from snap import client, util
from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Slot, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCharts import *


class Ui(QWidget):
    def __init__(self):
        super(Ui, self).__init__()
        self.resize(900, 700)
        self.labels = []
        self.buttons = []
        layout = QGridLayout()
        for i in range(6):
            for j in range(4):
                label = QLabel()
                label.setFixedSize(30, 30)
                label.setStyleSheet("background-color:gray;border-radius:15px;")
                self.labels.append(label)
                layout.addWidget(label, i, j)
        frame = QFrame(self)
        frame.resize(800, 400)
        frame.setLayout(layout)

        self.config = configparser.ConfigParser()
        self.config.read('ini', encoding='utf-8')
        buttons_name = self.config.options("DO")
        btn_layout = QGridLayout()
        for i, val in enumerate(buttons_name):
            btn = QPushButton(val)
            btn.pressed.connect(self.press_event)
            btn.released.connect(self.release_event)
            btn.setFixedSize(60, 30)
            btn_layout.addWidget(btn, i % 2, i // 2)
        frame2 = QFrame(self)
        frame2.resize(800, 300)
        frame2.move(0, 410)
        frame2.setLayout(btn_layout)

        self.star_btn = QPushButton('start', self)
        self.star_btn.move(30, 650)
        self.star_btn.clicked.connect(self.auto_do)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_data)

    def change_label_color(self, data):
        bytes = data
        self.labels[0].setStyleSheet("background-color:green;border-radius:15px;") if util.get_bool(bytes, 0, 0) else \
        self.labels[0].setStyleSheet("background-color:red;border-radius:15px;")
        self.labels[1].setStyleSheet("background-color:green;border-radius:15px;") if util.get_bool(bytes, 0, 1) else \
        self.labels[1].setStyleSheet("background-color:red;border-radius:15px;")
        self.labels[2].setStyleSheet("background-color:green;border-radius:15px;") if util.get_bool(bytes, 0, 2) else \
        self.labels[2].setStyleSheet("background-color:red;border-radius:15px;")
        self.labels[3].setStyleSheet("background-color:green;border-radius:15px;") if util.get_bool(bytes, 0, 3) else \
        self.labels[3].setStyleSheet("background-color:red;border-radius:15px;")
        self.labels[4].setStyleSheet("background-color:green;border-radius:15px;") if util.get_bool(bytes, 0, 4) else \
        self.labels[4].setStyleSheet("background-color:red;border-radius:15px;")
        self.labels[5].setStyleSheet("background-color:green;border-radius:15px;") if util.get_bool(bytes, 0, 5) else \
        self.labels[5].setStyleSheet("background-color:red;border-radius:15px;")

    def paintEvent(self, event) -> None:
        super(Ui, self).paintEvent(event)
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(Qt.green)
        painter.setPen(pen)
        for i in range(5):
            y = 30 + 50 * i
            painter.drawLine(10, y, 800, y)
        painter.end()


class FuncToolsUi(Ui):
    def __init__(self):
        super(FuncToolsUi, self).__init__()

        self.plc = client.Client()
        self.plc.set_connection_type(3)
        self.bytesarry = bytearray(14)
        try:
            self.plc.connect(self.config.get("PLC", "host"), 0, 1)
        except:
            self.flag = False
        else:
            self.flag = True
            self.timer.start(500)

    def read_data(self):
        bytes = self.plc.db_read(1, 0, 10)
        self.change_label_color(bytes)

    @Slot()
    def btn_click(self):
        btn_name = self.sender().text()

        id = self.config.getint("DO", btn_name)
        # print(btn_name,id)

    def press_event(self):
        txt = self.sender().text()
        id = self.config.getint("DO", txt) % 8
        count = self.config.getint("DO", txt) // 8
        util.set_bool(self.bytesarry, 10 + count, id, 1)
        self.plc.db_write(1, 0, self.bytesarry)
        print(txt, self.config.getint("DO", txt))

    def release_event(self):
        txt = self.sender().text()
        id = self.config.getint("DO", txt) % 8
        count = self.config.getint("DO", txt) // 8
        util.set_bool(self.bytesarry, 10 + count, id, 0)
        self.plc.db_write(1, 0, self.bytesarry)

    def auto_do(self):
        orders = eval(self.config.get("order", "启动顺序"))
        # [('制砂主机', 2), ('提升机', 3), ('震动筛', 4), ('上料皮带机', 5)]
        data = sorted([(v[1], v[0]) for v in orders])
        device = [tex[1] for tex in data]  # 启动顺序
        print(device)
        for i in device:
            addr = self.config.getint("DO", i) % 8
            step = self.config.getint("DO", i) // 8
            util.set_bool(self.bytesarry, 10 + step, addr, True)
            self.plc.db_write(1, 0, self.bytesarry)
            time.sleep(2)
            util.set_bool(self.bytesarry, 10 + step, addr, False)  # 复位
            self.plc.db_write(1, 0, self.bytesarry)