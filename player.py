import os
import time

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDir, pyqtSignal, QThread
from PyQt5.QtWidgets import QFileDialog, QMainWindow

from utils import image_helper
from video_player import Ui_MainWindow
from video_sources.file_video_source import FileVideoSource
import pickle


class Player(QThread):
    list_of_dict_signals = pyqtSignal(object, int, str)

    def __init__(self, parent, video_time_slider):
        QThread.__init__(self, parent)
        self.running = False
        self.video_time_slider = video_time_slider
        self.video_source = None
        self.reversed = False
        self.last_skip = 0
        self.skip = -1
        self.goto_frame_index = -1
        # self.video_time_slider.valueChanged.connect(self.sliderChanged)
        self.video_time_slider.sliderMoved.connect(self.sliderMoved)
        self.video_time_slider.sliderPressed.connect(self.sldDisconnect)
        self.video_time_slider.sliderReleased.connect(self.sldReconnect)
        self.timer_id = -1
        self._prev = 0
        self.slow_motion = False
        self.active_frame = None
        self.speed = 1


    def sldDisconnect(self):
        self.pause()

    def sldReconnect(self):
        self.toggle()

    # def sliderChanged(self):
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

            ok, frame = self.video_source.next(0)
            if ok:
                self.list_of_dict_signals.emit(frame, self.video_source.get_current_frame_index(), self.video_source.get_time_text())
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


    def run(self):
        prev = 0
        self.running = True
        while self.running:
            try:
                if self.goto_frame_index >= 0:
                    ok, frame = self.video_source.goto(self.goto_frame_index)
                    if ok:
                        self.list_of_dict_signals.emit(frame, self.video_source.get_current_frame_index(), self.video_source.get_time_text())
                    self.goto_frame_index = -1
                elif self.skip >= 0:
                    time_elapsed = time.time() - prev
                    if self.slow_motion:
                        time_elapsed *= 0.1
                    if self.speed != 1:
                        time_elapsed *= self.speed
                    if time_elapsed > 1. / self.video_source.fps:
                        prev = time.time()
                        ok, frame = self.video_source.previous(self.skip) if self.reversed else self.video_source.next(self.skip)
                        if ok:
                            self.list_of_dict_signals.emit(frame, self.video_source.get_current_frame_index(), self.video_source.get_time_text())
            except:
                self.pause()
