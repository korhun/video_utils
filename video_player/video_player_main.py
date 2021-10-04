import os
import time

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QDir, QSettings, QSize, QPoint
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QShortcut

from player import Player
from utils import image_helper, file_helper
from video_player import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    resized = QtCore.pyqtSignal()

    def resizeEvent(self, event):
        self.resized.emit()
        return super(QMainWindow, self).resizeEvent(event)

    # def on_window_resized(self):
    #     pass

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)
        self.setupUi(self)

        # self.resized.connect(self.on_window_resized)

        self.pushButton_fast_left.setIcon(QtGui.QIcon('img/fast_play_left.png'))
        self.pushButton_left.setIcon(QtGui.QIcon('img/play_left.png'))
        self.pushButton_pause.setIcon(QtGui.QIcon('img/pause.png'))
        self.pushButton_right.setIcon(QtGui.QIcon('img/play_right.png'))
        self.pushButton_fast_right.setIcon(QtGui.QIcon('img/fast_play_right.png'))
        self.pushButton_save.setIcon(QtGui.QIcon('img/snapshot.png'))
        self.pushButton_output_dir.setIcon(QtGui.QIcon('img/folder.png'))

        # self.comboBox_speed.addItem("0.1")
        # self.comboBox_speed.addItem("0.2")
        # self.comboBox_speed.addItem("0.5")
        # self.comboBox_speed.addItem("Normal")
        # self.comboBox_speed.addItem("2")
        # self.comboBox_speed.addItem("5")
        # self.comboBox_speed.addItem("10")
        # self.comboBox_speed.setCurrentIndex(3)
        # self.comboBox_speed.activated[str].connect(self.on_comboBox_speed_changed)

        self.pushButton_fast_left.clicked.connect(self.clicked_fast_left)
        self.pushButton_left.clicked.connect(self.clicked_left)
        self.pushButton_pause.clicked.connect(self.clicked_pause)
        self.pushButton_right.clicked.connect(self.clicked_right)
        self.pushButton_fast_right.clicked.connect(self.clicked_fast_right)

        self.actionFile.triggered.connect(self.clicked_file)
        self.actionOutput_Dir.triggered.connect(self.clicked_output_dir)
        self.pushButton_output_dir.clicked.connect(self.clicked_output_dir)

        self.actionSave_Current.setShortcut('Ctrl+S')

        self.actionSave_Current.triggered.connect(self.save_current_frame)
        self.pushButton_save.clicked.connect(self.save_current_frame)

        # self.image_view.setScaledContents(True)
        self.image_view.mousePressEvent = self.on_image_view_mouse_pressed
        self.image_view.setMinimumSize(1, 1)

        self.output_dir = None
        self.player = Player(self, self.video_time_slider, self.video_speed_slider, self.speed_spin_box)
        self.player.list_of_dict_signals.connect(self._load_frame)
        self.player.start()

        self.just_loaded = 0

        self.settings = QSettings(QSettings.IniFormat, QSettings.SystemScope, 'Orientis', 'video_player')
        last_video = self.settings.value("last_video", "")
        if os.path.isfile(last_video):
            self.load_video(last_video)

        self.settings.setFallbacksEnabled(False)  # File only, not registry
        self.resize(self.settings.value("size", QSize(800, 800)))
        self.move(self.settings.value("pos", QPoint(200, 200)))

    def closeEvent(self, e):
        self.player.running = False
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())

    # def on_comboBox_speed_changed(self, text):
    #     if text == "Normal":
    #         self.player.set_speed(1)
    #     else:
    #         self.player.set_speed(float(text))

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
            self.player.shift_pressed = True

        elif e.key() == Qt.Key_Left:
            self.player.play_previous_frame()
        elif e.key() == Qt.Key_Right:
            self.player.play_next_frame()
        elif e.key() == Qt.Key_Down:
            self.player.play_previous_frame(5)
        elif e.key() == Qt.Key_Up:
            self.player.play_next_frame(5)

    def key_released(self, e):
        if e.key() == Qt.Key_Shift:
            self.player.shift_pressed = False

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
        self.select_file()

    def select_file(self):
        self.player.pause()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setWindowTitle('Open Video File')
        # dialog.setNameFilter('Video Fle (*.mov *.avi *.mp4)')
        # dialog.setFilter(QDir.Files)
        last_dir = self.settings.value("last_dir", "")
        if os.path.isdir(last_dir):
            dialog.setDirectory(last_dir)
        if dialog.exec_():
            dir_name = dialog.directory().absolutePath()
            self.settings.setValue("last_dir", dir_name)
            file_names = dialog.selectedFiles()
            if file_names and len(file_names) > 0:
                self.load_video(file_names[0])

    def load_video(self, file_name):
        if self.player.load_video(file_name):
            self.just_loaded = 1
            self.settings.setValue("last_video", file_name)

    def clicked_output_dir(self):
        self.select_out_dir()

    def select_out_dir(self):
        self.player.pause()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setWindowTitle('Select Output Directory')
        last_out_dir = self.settings.value("last_out_dir", "")
        if os.path.isdir(last_out_dir):
            dialog.setDirectory(last_out_dir)
        if dialog.exec_():
            dir_name = dialog.directory().absolutePath()
            self.settings.setValue("last_out_dir", dir_name)
            self.output_dir = dir_name

    def save_current_frame(self):
        if self.output_dir is None or not os.path.isdir(self.output_dir):
            self.select_out_dir()
        if self.output_dir is not None and os.path.isdir(self.output_dir):
            frame, index = self.player.get_current_frame_and_index()
            if frame is not None:
                fn = file_helper.path_join(self.output_dir, str(index) + ".png")
                cv2.imwrite(fn, frame)

    def _load_frame(self, frame, current_frame_index, time_text):
        w, h = self.image_view.width(), self.image_view.height()
        if self.just_loaded == 1:
            self.just_loaded = 2
            w, h = frame.shape[1], frame.shape[0]
            self.image_view.setMinimumSize(w, h)
        elif self.just_loaded == 2:
            self.just_loaded = 0
            self.image_view.setMinimumSize(1, 1)

        h1, w1 = frame.shape[:2]
        image = QtGui.QImage(frame.data, w1, h1, QtGui.QImage.Format_BGR888)
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio)
        self.image_view.setPixmap(pixmap)

        self.video_time_slider.setValue(current_frame_index)
        self.video_time_label.setText(time_text)


def show_video_player():
    import sys

    app = QtWidgets.QApplication(sys.argv)

    translator = QtCore.QTranslator()
    translator.load("video_player-tr.qm")
    app.installTranslator(translator)

    win = MainWindow()
    win.setWindowIcon(QtGui.QIcon("img/video.png"))
    win.show()


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
