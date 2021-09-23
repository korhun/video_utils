import os
import time

import cv2
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
        self.active_frame = None
        self.just_loaded = 0

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
            self.just_loaded = 1

            ok, frame = self.video_source.next(0)
            if ok:
                self._load_frame(frame)
                self.play_right(True)
                return True
        except:
            self.pause()
        return False

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

    def _load_frame(self, frame):
        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_BGR888)

        w, h = self.image_view.width(), self.image_view.height()
        if self.just_loaded == 1:
            self.just_loaded = 2
            w, h = frame.shape[1], frame.shape[0]
            self.image_view.setMinimumSize(w, h)
            # self.image_view.setSize(w, h)
        elif self.just_loaded == 2:
            self.just_loaded = 0
            self.image_view.setMinimumSize(1, 1)

        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio)
        self.image_view.setPixmap(pixmap)

        self.video_time_slider.setValue(self.video_source.get_current_frame_index())
        self.video_time_label.setText(self.video_source.get_time_text())

    def run(self):
        prev = 0
        while True:
            try:
                if self.goto_frame_index >= 0:
                    ok, frame = self.video_source.goto(self.goto_frame_index)
                    if ok:
                        self._load_frame(frame)
                        # image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
                        # self.image_view.setPixmap(QtGui.QPixmap.fromImage(image))
                        # self.video_time_slider.setValue(self.video_source.get_current_frame_index())
                        # self.video_time_label.setText(self.video_source.get_time_text())
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
                            self._load_frame(frame)
                            # # self.active_frame = frame.copy()
                            # # frame = cv2.resize(frame, (self.image_view.width(), self.image_view.height()))
                            #
                            # # image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
                            # image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],  QtGui.QImage.Format_BGR888)
                            # # image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],  QtGui.QImage.)
                            #
                            # # Format_A2BGR30_Premultiplied = 20
                            # # Format_A2RGB30_Premultiplied = 22
                            # # Format_Alpha8 = 23
                            # # Format_ARGB32 = 5
                            # # Format_ARGB32_Premultiplied = 6
                            # # Format_ARGB4444_Premultiplied = 15
                            # # Format_ARGB6666_Premultiplied = 10
                            # # Format_ARGB8555_Premultiplied = 12
                            # # Format_ARGB8565_Premultiplied = 8
                            # # Format_BGR30 = 19
                            # # Format_BGR888 = 29
                            # # Format_Grayscale16 = 28
                            # # Format_Grayscale8 = 24
                            # # Format_Indexed8 = 3
                            # # Format_Invalid = 0
                            # # Format_Mono = 1
                            # # Format_MonoLSB = 2
                            # # Format_RGB16 = 7
                            # # Format_RGB30 = 21
                            # # Format_RGB32 = 4
                            # # Format_RGB444 = 14
                            # # Format_RGB555 = 11
                            # # Format_RGB666 = 9
                            # # Format_RGB888 = 13
                            # # Format_RGBA64 = 26
                            # # Format_RGBA64_Premultiplied = 27
                            # # Format_RGBA8888 = 17
                            # # Format_RGBA8888_Premultiplied = 18
                            # # Format_RGBX64 = 25
                            # # Format_RGBX8888 = 16
                            # # InvertRgb = 0
                            # # InvertRgba = 1
                            #
                            # # self.image_view.setPixmap(QtGui.QPixmap.fromImage(image))
                            #
                            # w, h = self.image_view.width(), self.image_view.height()
                            # if self.just_loaded == 1:
                            #     self.just_loaded = 2
                            #     w, h = frame.shape[1], frame.shape[0]
                            #     self.image_view.setMinimumSize(w, h)
                            # elif self.just_loaded == 2:
                            #     self.just_loaded = 0
                            #     self.image_view.setMinimumSize(1, 1)
                            #
                            # pixmap = QtGui.QPixmap.fromImage(image)
                            # pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio)
                            # self.image_view.setPixmap(pixmap)

                            # self.video_time_slider.setValue(self.video_source.get_current_frame_index())
                            # self.video_time_label.setText(self.video_source.get_time_text())
                time.sleep(0.01)
            except:
                self.pause()
