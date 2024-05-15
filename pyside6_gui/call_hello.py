import sys
from PySide6 import QtCore, QtWidgets, QtGui

import helloworld


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        ui = helloworld.Ui_Form()  # 实例化UI对象
        ui.setupUi(self)  # 初始化

    @QtCore.Slot()  # 槽函数用它装饰
    def login(self):  # 在Qt Designer中为登录按钮命名的槽函数；
        print("你点击了登录")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
