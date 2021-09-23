import os
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtWidgets import QFileDialog, QMainWindow

from player import Player
from video_player import Ui_MainWindow
from video_sources.file_video_source import FileVideoSource
import pickle


class MainWindow(QMainWindow, Ui_MainWindow):
    resized = QtCore.pyqtSignal()

    def resizeEvent(self, event):
        self.resized.emit()
        return super(QMainWindow, self).resizeEvent(event)

    def on_window_resized(self):
        # self.player.pause()
        pass

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)
        self.setupUi(self)

        self.resized.connect(self.on_window_resized)

        self.pushButton_fast_left.setIcon(QtGui.QIcon('img/fast_play_left.png'))
        self.pushButton_left.setIcon(QtGui.QIcon('img/play_left.png'))
        self.pushButton_pause.setIcon(QtGui.QIcon('img/pause.png'))
        self.pushButton_right.setIcon(QtGui.QIcon('img/play_right.png'))
        self.pushButton_fast_right.setIcon(QtGui.QIcon('img/fast_play_right.png'))
        self.pushButton_save.setIcon(QtGui.QIcon('img/save.png'))
        self.pushButton_output_dir.setIcon(QtGui.QIcon('img/folder.png'))

        self.comboBox_speed.addItem("0.25")
        self.comboBox_speed.addItem("0.5")
        self.comboBox_speed.addItem("0.75")
        self.comboBox_speed.addItem("Normal")
        self.comboBox_speed.addItem("1.25")
        self.comboBox_speed.addItem("1.5")
        self.comboBox_speed.addItem("1.75")
        self.comboBox_speed.addItem("2")
        self.comboBox_speed.setCurrentIndex(3)

        self.pushButton_fast_left.clicked.connect(self.clicked_fast_left)
        self.pushButton_left.clicked.connect(self.clicked_left)
        self.pushButton_pause.clicked.connect(self.clicked_pause)
        self.pushButton_right.clicked.connect(self.clicked_right)
        self.pushButton_fast_right.clicked.connect(self.clicked_fast_right)

        self.actionFile.triggered.connect(self.clicked_file)
        self.actionOutput_Dir.triggered.connect(self.clicked_output_dir)

        # self.image_view.setScaledContents(True)
        self.image_view.mousePressEvent = self.on_image_view_mouse_pressed
        self.image_view.setMinimumSize(1, 1)

        self.output_dir = None
        self.player = Player(self.image_view, self.video_time_slider, self.video_time_label)
        self.player.start()
        try:
            with open(r"__last_video.pickle", "rb") as last_video:
                last_video_file_name = pickle.load(last_video)
                if os.path.isfile(last_video_file_name):
                    self.load_video(last_video_file_name)
        except:
            pass

    def on_image_view_mouse_pressed(self, _):
        self.player.toggle()

    def keyPressEvent(self, event):
        # if not event.isAutoRepeat():
        self.key_pressed(event)

    def keyReleaseEvent(self, event):
        self.key_released(event)

    def key_pressed(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_7:
            self.player.play_left_fast(True)
        elif e.key() == Qt.Key_4:
            self.player.play_left(True)
        elif e.key() == Qt.Key_5:
            self.player.pause()
        elif e.key() == Qt.Key_8:
            self.player.pause()

        elif e.key() == Qt.Key_Space:
            self.player.toggle()

        elif e.key() == Qt.Key_6:
            self.player.play_right(True)
        elif e.key() == Qt.Key_9:
            self.player.play_right_fast(True)
        elif e.key() == Qt.Key_Shift:
            self.player.slow_motion = True

        elif e.key() == Qt.Key_Left:
            self.player.play_previous_frame()
        elif e.key() == Qt.Key_Right:
            self.player.play_next_frame()
        elif e.key() == Qt.Key_Down:
            self.player.play_previous_frame(5)
        elif e.key() == Qt.Key_Up:
            self.player.play_next_frame(5)

        # else:
        #     print(e.key())

    def key_released(self, e):
        if e.key() == Qt.Key_Shift:
            self.player.slow_motion = False

        # elif e.key() == Qt.Key_Space:
        #     self.player.toggle()

        # elif e.key() == Qt.Key_Left:
        #     self.player.play_previous_frame()
        # elif e.key() == Qt.Key_Right:
        #     self.player.play_next_frame()
        # elif e.key() == Qt.Key_Down:
        #     self.player.play_previous_frame(5)
        # elif e.key() == Qt.Key_Up:
        #     self.player.play_next_frame(5)

    def clicked_fast_left(self):
        self.player.play_left_fast()

    def clicked_left(self):
        self.player.play_left()

    def clicked_pause(self):
        self.player.pause()

    def clicked_right(self):
        self.player.play_right()

    def clicked_fast_right(self):
        self.player.play_right_fast()

    def clicked_file(self):
        file_names = self.select_file()
        if file_names and len(file_names) > 0:
            self.load_video(file_names[0])

    def select_file(self):
        self.player.pause()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setWindowTitle('Open Video File')
        # dialog.setNameFilter('Video Fle (*.mov *.avi *.mp4)')
        # dialog.setFilter(QDir.Files)
        try:
            with open(r"__last_dir.pickle", "rb") as load_file:
                dialog.setDirectory(pickle.load(load_file))
        except:
            pass
        if dialog.exec_():
            dir_name = dialog.directory().dirName()
            with open(r"__last_dir.pickle", "wb") as save_file:
                pickle.dump(dir_name, save_file)
            return dialog.selectedFiles()

    def load_video(self, file_name):
        if self.player.load_video(file_name):
            with open(r"__last_video.pickle", "wb") as save_file:
                pickle.dump(file_name, save_file)

    def clicked_output_dir(self):
        dir_name = self.select_dir()
        if dir_name is not None and os.path.isdir(dir_name):
            self.output_dir = dir_name

    def select_dir(self):
        self.player.pause()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setWindowTitle('Select Output Directory')
        try:
            with open(r"__last_out_dir.pickle", "rb") as load_file:
                dialog.setDirectory(pickle.load(load_file))
        except:
            pass
        if dialog.exec_():
            dir_name = dialog.directory().dirName()
            with open(r"__last_out_dir.pickle", "wb") as save_file:
                pickle.dump(dir_name, save_file)
            return dir_name


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    translator = QtCore.QTranslator()
    translator.load("video_player-tr.qm")
    app.installTranslator(translator)

    win = MainWindow()
    win.setWindowIcon(QtGui.QIcon("img/video.png"))
    win.show()
    sys.exit(app.exec_())
