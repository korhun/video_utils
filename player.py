import os
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtWidgets import QFileDialog, QMainWindow

from video_player import Ui_MainWindow
from video_sources.file_video_source import FileVideoSource
import pickle


class Player(QtCore.QThread):
    def __init__(self, image_view, video_time_slider, video_time_label):
        self.image_view = image_view
        self.video_time_slider = video_time_slider
        self.video_time_label = video_time_label
        self.video_source = None
        self.reversed = False
        self.last_skip = 0
        self.skip = -1
        self.goto_frame_index = -1
        QtCore.QThread.__init__(self)
        # self.video_time_slider.valueChanged.connect(self.sliderChanged)
        self.video_time_slider.sliderMoved.connect(self.sliderMoved)
        self.video_time_slider.sliderPressed.connect(self.sldDisconnect)
        self.video_time_slider.sliderReleased.connect(self.sldReconnect)
        self.timer_id = -1
        self._prev = 0
        self.slow_motion = False

    def sldDisconnect(self):
        # self.sender().valueChanged.disconnect()
        self.pause()

    def sldReconnect(self):
        # self.sender().valueChanged.connect(self.sliderChanged)
        # self.sender().valueChanged.emit(self.sender().value())
        self.pause()

    # def sliderChanged(self):
    #     # print(self.sender().objectName() + " : " + str(self.sender().value()))
    #     # if self.skip == -1:
    #     #     self.goto_frame_index = self.sender().value()
    #     pass

    def sliderMoved(self):
        if self.skip == -1 and self.goto_frame_index == -1:
            time_elapsed = time.time() - self._prev
            if time_elapsed > 0.2:
                self._prev = time.time()
                self.goto_frame_index = self.sender().value()

    def load_video(self, file_name):
        try:
            self.video_source = FileVideoSource(file_name)
            self.video_time_slider.setMaximum(self.video_source.frame_count)
            self.video_time_slider.setTickInterval(1)
            self.video_time_slider.setValue(self.video_source.get_current_frame_index())
            self.play_right(True)
        except:
            self.pause()

    def play_next_frame(self, skip=1):
        self.pause()
        self.goto_frame_index = self.video_source.get_current_frame_index() + (5 * skip if self.slow_motion else skip)

    def play_previous_frame(self, skip=1):
        self.pause()
        self.goto_frame_index = self.video_source.get_current_frame_index() - (5 * (skip + 1) + 1 if self.slow_motion else skip + 1)

    def play_left_fast(self, forced=False):
        if not forced and self.skip > 0 and self.reversed:
            self.pause()
        else:
            self.reversed = True
            self.skip = 5

    def play_left(self, forced=False):
        if not forced and self.skip == 0 and self.reversed:
            self.pause()
        else:
            self.reversed = True
            self.skip = 0

    def pause(self):
        if self.skip != -1:
            self.last_skip = self.skip
            self.skip = -1

    def toggle(self):
        if self.skip == -1:
            self.skip = self.last_skip
        else:
            self.pause()

    def play_right(self, forced=False):
        if not forced and self.skip == 0 and not self.reversed:
            self.pause()
        else:
            self.reversed = False
            self.skip = 0

    def play_right_fast(self, forced=False):
        if not forced and self.skip > 0 and not self.reversed:
            self.pause()
        else:
            self.reversed = False
            self.skip = 5

    def run(self):
        prev = 0
        while True:
            try:
                if self.goto_frame_index >= 0:
                    ok, frame = self.video_source.goto(self.goto_frame_index)
                    if ok:
                        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
                        self.image_view.setPixmap(QtGui.QPixmap.fromImage(image))
                        self.video_time_slider.setValue(self.video_source.get_current_frame_index())
                        self.video_time_label.setText(self.video_source.get_time_text())
                    self.goto_frame_index = -1
                elif self.skip >= 0:
                    time_elapsed = time.time() - prev

                    # modifiers = QtWidgets.QApplication.keyboardModifiers()
                    # if modifiers == QtCore.Qt.ShiftModifier:  # shift pressed
                    if self.slow_motion:
                        time_elapsed *= 0.1

                    if time_elapsed > 1. / self.video_source.fps:
                        prev = time.time()
                        ok, frame = self.video_source.previous(self.skip) if self.reversed else self.video_source.next(self.skip)
                        if ok:
                            image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()

                            self.image_view.setPixmap(QtGui.QPixmap.fromImage(image))
                            # pixmap = QtGui.QPixmap.fromImage(image)
                            # pixmap = pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio)
                            # self.image_view.setPixmap(pixmap)

                            self.video_time_slider.setValue(self.video_source.get_current_frame_index())
                            self.video_time_label.setText(self.video_source.get_time_text())
            except:
                self.pause()
