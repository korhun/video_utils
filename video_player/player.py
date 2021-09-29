import math
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

    def __init__(self, parent, time_slider, speed_slider, speed_spin_box):
        QThread.__init__(self, parent)
        self.running = False
        self.time_slider = time_slider
        self.speed_slider = speed_slider
        self.speed_spin_box = speed_spin_box
        self.video_source = None
        self.goto_frame_index = -1

        # self.time_slider.valueChanged.connect(self.time_slider_value_changed)
        self.time_slider.sliderMoved.connect(self.time_slider_moved)
        self.time_slider.sliderPressed.connect(self.time_slider_pressed)
        self.time_slider.sliderReleased.connect(self.time_slider_released)

        self.speed_slider.setMaximum(100)
        self.speed_slider.setMinimum(-100)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.setValue(0)
        # self.speed_slider.valueChanged.connect(self.speed_slider_value_changed)
        self.speed_slider.sliderMoved.connect(self.speed_slider_moved)

        self.speed_spin_box.valueChanged.connect(self.speed_spin_box_value_changed)

        self.current_frame = None
        self.current_frame_index = None

        self.timer_id = -1
        self._prev = 0
        self.shift_pressed = False
        self.active_frame = None
        self._speed = 0
        self._speed_last = 1
        self._set_speed_is_active = False

    def time_slider_moved(self):
        if self._speed == 0 and self.goto_frame_index == -1:
            time_elapsed = time.time() - self._prev
            if time_elapsed > 0.2:
                self._prev = time.time()
                self.goto_frame_index = self.sender().value()

    def time_slider_pressed(self):
        self.pause()

    def time_slider_released(self):
        self.toggle()

    # def time_slider_value_changed(self):
    #     pass

    # def speed_slider_value_changed(self):
    #     pass

    def speed_spin_box_value_changed(self):
        if not self._set_speed_is_active:
            self.set_speed(self.speed_spin_box.value())

    def speed_slider_moved(self):
        if not self._set_speed_is_active:
            slider_val = self.speed_slider.value()
            speed = math.pow(abs(slider_val) / 20.0, 2.0)
            if slider_val >= 0:
                self.set_speed(speed)
            else:
                self.set_speed(-speed)

    def set_speed(self, speed):
        if not self._set_speed_is_active:
            try:
                self._set_speed_is_active = True
                speed = round(speed, 2)
                if speed != self._speed:
                    if self._speed != 0:
                        self._speed_last = self._speed
                    self._speed = speed

                    slider_val = math.pow(abs(speed), 1.0 / 2.0) * 20.0
                    if speed >= 0:
                        self.speed_slider.setValue(slider_val)
                    else:
                        self.speed_slider.setValue(-slider_val)
            finally:
                self._set_speed_is_active = False
                self.speed_spin_box.setValue(self._speed)

    def load_video(self, file_name):
        try:
            self.video_source = FileVideoSource(file_name)
            self.time_slider.setMaximum(self.video_source.frame_count)
            self.time_slider.setTickInterval(1)
            self.time_slider.setValue(self.video_source.get_current_frame_index())

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
        self.goto_frame_index = self.video_source.get_current_frame_index() + (5 * skip if self.shift_pressed else skip)

    def play_previous_frame(self, skip=1):
        self.pause()
        self.goto_frame_index = self.video_source.get_current_frame_index() - (5 * (skip + 1) + 1 if self.shift_pressed else skip + 1)

    def _play(self, forced, speed):
        if forced:
            self.set_speed(speed)
        else:
            if self._speed == speed:
                self.pause()
            else:
                self.set_speed(speed)

    def play_left_fast(self, forced=False):
        self._play(forced, -5)

    def play_left(self, forced=False):
        self._play(forced, -1)

    def pause(self):
        if self._speed != 0:
            self.set_speed(0)

    def toggle(self):
        if self._speed == 0:
            self.set_speed(self._speed_last)
        else:
            self.set_speed(0)

    def play_right(self, forced=False):
        self._play(forced, 1)

    def play_right_fast(self, forced=False):
        self._play(forced, 5)

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
                elif self._speed != 0:
                    abs_speed = abs(self._speed)
                    time_elapsed = time.time() - prev
                    if self.shift_pressed:
                        time_elapsed *= 0.1
                    if abs_speed != 1:
                        time_elapsed *= abs_speed
                    if time_elapsed > 1. / self.video_source.fps:
                        prev = time.time()
                        skip = max(1, int(abs_speed))
                        ok, frame = self.video_source.previous(skip) if self._speed < 0 else self.video_source.next(skip)
                        if ok:
                            self.current_frame = frame
                            self.current_frame_index = self.video_source.get_current_frame_index()
                            self.list_of_dict_signals.emit(frame, self.video_source.get_current_frame_index(), self.video_source.get_time_text())
                        else:
                            self.pause()
            except:
                self.pause()

    def get_current_frame_and_index(self):
        return self.current_frame, self.current_frame_index
