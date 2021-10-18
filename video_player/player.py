import math
import time

from PyQt5.QtCore import Qt, QDir, pyqtSignal, QThread

if __name__ == 'player':
    from video_sources.file_video_source import FileVideoSource
else:
    from .video_sources.file_video_source import FileVideoSource


class Player(QThread):
    list_of_dict_signals = pyqtSignal(object, int, str)
    video_start_signal = pyqtSignal()
    video_end_signal = pyqtSignal()

    def __init__(self, parent, time_slider, speed_dial, speed_spin_box):
        QThread.__init__(self, parent)
        self.running = False
        self.time_slider = time_slider
        self.speed_dial = speed_dial
        self.speed_spin_box = speed_spin_box
        self.video_source = None
        self.goto_frame_index = -1

        self.speed_spin_box.setKeyboardTracking(False)

        self.time_slider.valueChanged.connect(self.time_slider_value_changed)
        # self.time_slider.sliderMoved.connect(self.time_slider_moved)
        self.time_slider.sliderPressed.connect(self.time_slider_pressed)
        self.time_slider.sliderReleased.connect(self.time_slider_released)

        self.speed_dial.setMaximum(100)
        self.speed_dial.setMinimum(-100)
        self.speed_dial.setSingleStep(2)

        self.speed_dial.setValue(0)
        self.speed_dial.valueChanged.connect(self.speed_dial_value_changed)

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
        self._slider_last_speed = 0
        self._frame_count = 0

    # def time_slider_moved(self):
    #     val = self.sender().value()
    #     if self.current_frame_index != val:
    #         self.goto_frame_index = val

    def time_slider_pressed(self):
        self._slider_last_speed = self._speed
        self.pause()

    def time_slider_released(self):
        self.set_speed(self._slider_last_speed)

    def time_slider_value_changed(self):
        val = self.sender().value()
        if self.current_frame_index != val:
            self.goto_frame_index = val

    def speed_spin_box_value_changed(self):
        if not self._set_speed_is_active:
            self.set_speed(self.speed_spin_box.value())

    def speed_dial_value_changed(self):
        if not self._set_speed_is_active:
            slider_val = self.speed_dial.value()
            speed = math.pow(abs(slider_val) / 20.0, 2.0)
            if slider_val >= 0:
                self.set_speed(speed)
            else:
                self.set_speed(-speed)

    def speed_last(self):
        return self._speed_last

    def speed(self):
        return self._speed

    def set_speed(self, speed):
        if not self._set_speed_is_active:
            try:
                self._set_speed_is_active = True
                speed = round(speed, 2)
                if speed != self._speed:
                    self._speed_last = self._speed
                    self._speed = speed

                    slider_val = math.pow(abs(speed), 1.0 / 2.0) * 20.0
                    if speed >= 0:
                        self.speed_dial.setValue(slider_val)
                    else:
                        self.speed_dial.setValue(-slider_val)
            finally:
                self._set_speed_is_active = False
                self.speed_spin_box.setValue(self._speed)

    def get_frame_count(self):
        return self._frame_count

    def load_video(self, file_name):
        try:
            self.video_source = FileVideoSource(file_name)
            self._frame_count = self.video_source.frame_count
            self.time_slider.setMaximum(self._frame_count)
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

    def goto_frame(self, frame_index):
        self.goto_frame_index = frame_index

    def play_next_frame(self, skip=1):
        self.pause()
        current_index = self.video_source.get_current_frame_index()
        target_index = current_index + (5 * skip if self.shift_pressed else skip)
        self.goto_frame_index = target_index

    def play_previous_frame(self, skip=1):
        self.pause()
        current_index = self.video_source.get_current_frame_index()
        target_index = current_index - (5 * skip if self.shift_pressed else skip)
        self.goto_frame_index = target_index

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
            self.pause()

    def play_right(self, forced=False):
        self._play(forced, 1)

    def play_right_fast(self, forced=False):
        self._play(forced, 5)

    def _emit(self, frame):
        self.current_frame = frame
        self.current_frame_index = self.video_source.get_current_frame_index()
        self.list_of_dict_signals.emit(frame, self.current_frame_index, self.video_source.get_time_text())

    def run(self):
        prev = 0
        self.running = True
        while self.running:
            try:
                if self.goto_frame_index >= 0 and self.goto_frame_index != self.current_frame_index:
                    ok, frame = self.video_source.goto(self.goto_frame_index)
                    if ok:
                        self._emit(frame)
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
                            self._emit(frame)
                        else:
                            if self._speed < 0:
                                self.video_start_signal.emit()
                            else:
                                self.video_end_signal.emit()
                            self.pause()

                else:
                    time.sleep(0.1)
            except:
                self.pause()

    def get_current_frame_and_index(self):
        return self.current_frame, self.current_frame_index
