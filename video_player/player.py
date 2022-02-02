import math
import time
from typing import Optional

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QSlider

if __name__ == 'player':
    from video_sources.video_source import VideoSource
    from video_sources.file_video_source import FileVideoSource
    from video_sources.camera_video_source import CameraVideoSource
    from video_sources.stream_video_source import StreamVideoSource
else:
    from .video_sources.video_source import VideoSource
    from .video_sources.file_video_source import FileVideoSource
    from .video_sources.camera_video_source import CameraVideoSource
    from .video_sources.stream_video_source import StreamVideoSource


# noinspection PyBroadException
class Player(QThread):
    frame_changed_signal = pyqtSignal(object, int, str)
    video_start_signal = pyqtSignal()
    video_end_signal = pyqtSignal()
    speed_changed = pyqtSignal(int)

    def __init__(self, parent, time_slider: QSlider, speed_dial, speed_spin_box):
        QThread.__init__(self, parent)
        self._parent = parent
        self._running = False
        self.time_slider = time_slider
        self.speed_dial = speed_dial
        self.speed_spin_box = speed_spin_box
        self.video_source: Optional[VideoSource] = None
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
        self._run_counter = 0
        self._slider_ready = False
        self._fps = 0
        self._fps_div = 0

    # def time_slider_moved(self):
    #     val = self.sender().value()
    #     if self.current_frame_index != val:
    #         self.goto_frame(val)

    def time_slider_pressed(self):
        self._slider_ready = True
        self._slider_last_speed = self._speed
        self.pause()

    def time_slider_released(self):
        self.set_speed(self._slider_last_speed)

    def time_slider_value_changed(self):
        val = self.sender().value()
        if self._slider_ready and self.current_frame_index != val:
            self.goto_frame(val)

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

    # noinspection PyUnresolvedReferences
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
                    self.speed_changed.emit(self._speed)
            finally:
                self._set_speed_is_active = False
                self.speed_spin_box.setValue(self._speed)

    def get_frame_count(self):
        return self._frame_count

    def _update_fps(self):
        self._fps = self.video_source.fps()
        if self._fps <= 0:
            self._fps = 24
        self._fps_div = 1.0 / self._fps

    def load_video_file(self, file_name):
        try:
            self._parent.cursor_wait()
            self.stop()
            self.video_source = FileVideoSource(file_name)
            self._update_fps()
            self._frame_count = self.video_source.frame_count
            if self._frame_count > 0:
                self.time_slider.setVisible(True)
                self.time_slider.setMaximum(self._frame_count)
                self.time_slider.setTickInterval(1)
                self.time_slider.setValue(self.video_source.get_current_frame_index())
            else:
                self.time_slider.setVisible(False)

            time.sleep(0.1)
            ok, frame = self.video_source.next(0)
            if ok:
                self.goto_frame(0)
                self.play_right(True)
                return True
        except:
            self.pause()
        finally:
            self._parent.cursor_restore()
        return False

    def load_video_camera(self):
        try:
            self._parent.cursor_wait()
            self.stop()
            self.video_source = CameraVideoSource()
            self._frame_count = -1
            self._update_fps()
            self.time_slider.setVisible(False)
            ok, frame = self.video_source.next(0)
            if ok:
                self.goto_frame(0)
                self.play_right(True)
                return True
        except:
            self.pause()
        finally:
            self._parent.cursor_restore()
        return False

    def load_url(self, url, is_youtube):
        try:
            self._parent.cursor_wait()
            self.stop()
            self.video_source = StreamVideoSource(url, is_youtube)
            self._frame_count = -1
            self._update_fps()
            self.time_slider.setVisible(False)
            ok, frame = self.video_source.next(0)
            if ok:
                self.goto_frame(0)
                self.play_right(True)
                return True
        except:
            self.pause()
        finally:
            self._parent.cursor_restore()
        return False

    def stop(self):
        c = self._run_counter + 1
        self.pause()
        time.sleep(0.1)
        while c >= self._run_counter and self._running:
            self.pause()
            time.sleep(0.1)
        if self.video_source is not None:
            vs = self.video_source
            self.video_source = None
            time.sleep(0.1)
            vs.stop()
        self._slider_ready = False
        self.goto_frame_index = -1

    def release(self):
        self.stop()
        self._running = False

    def running(self):
        return self._running

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

    # noinspection PyUnresolvedReferences
    def _emit_frame(self, frame):
        if self.goto_frame_index < 0:
            self.current_frame = frame
            self.current_frame_index = self.video_source.get_current_frame_index()
            time_text = self.video_source.get_time_text()
            if self.goto_frame_index < 0:
                self.frame_changed_signal.emit(frame, self.current_frame_index, time_text)
                time.sleep(0.01)
                self._slider_ready = True

    # noinspection PyUnresolvedReferences
    def run(self):
        prev = 0
        self._running = True
        while self._running:
            try:
                if self.goto_frame_index >= 0 and self.goto_frame_index != self.current_frame_index:
                    goto_index = self.goto_frame_index
                    ok, frame = self.video_source.goto(goto_index)
                    if goto_index == self.goto_frame_index:
                        self.goto_frame_index = -1
                        if ok:
                            self._emit_frame(frame)
                else:
                    self.goto_frame_index = -1
                    if self._speed != 0:
                        abs_speed = abs(self._speed)
                        time_elapsed = time.time() - prev
                        if self.shift_pressed:
                            time_elapsed *= 0.1
                        if abs_speed != 1:
                            time_elapsed *= abs_speed
                        if time_elapsed > self._fps_div:
                            prev = time.time()
                            if self._frame_count <= 0:
                                ok, frame = self.video_source.next(0)
                                if frame is not None:
                                    self._emit_frame(frame)
                            else:
                                # skip = max(1, int(abs_speed))
                                skip = 0 if abs_speed < 2.0 else int(abs_speed)
                                ok, frame = self.video_source.previous(skip) if self._speed < 0 else self.video_source.next(skip)
                                if ok:
                                    self._emit_frame(frame)
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
            finally:
                self._run_counter += 1

    def get_current_frame_and_index(self):
        return self.current_frame, self.current_frame_index

    def get_current_time_text(self):
        return self.video_source.get_time_text()

    def enumerate_frames(self, start_index=0, step=0) -> (object, int):
        while self._speed != 0:
            self.pause()
        if step < 0:
            step = 0
        ok, frame = self.video_source.goto(start_index)
        while ok:
            self.current_frame = frame
            self.current_frame_index = self.video_source.get_current_frame_index()
            yield self.current_frame, self.current_frame_index
            ok, frame = self.video_source.next(step)

    def fps(self):
        return self._fps
