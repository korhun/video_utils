import time

import cv2

if __package__ is None or __package__ == '':
    from video_source import VideoSource
else:
    from .video_source import VideoSource


class CameraVideoSource(VideoSource):
    def __init__(self, mirror=True):
        self._mirror = mirror
        self._fps = 0
        self._current_frame_index = 1
        super(CameraVideoSource, self).__init__()
        self._set_capture()

    def _set_capture(self):
        self._capture = self._find_video_capture()
        self._fps = self._capture.get(cv2.CAP_PROP_FPS)

    def fps(self):
        return self._fps

    def reset(self):
        self.stop()
        self._set_capture()

    # returns ok, frame
    def next(self, skip=0):
        ok, frame = self._capture.read()
        self._current_frame_index += 1
        if ok and self._mirror:
            frame = cv2.flip(frame, 1)
        return ok, frame

    # returns ok, frame
    def previous(self, skip=0):
        return False, None

    # returns ok, frame
    def goto(self, frame_index):
        return False, None

    def stop(self):
        try:
            self._capture.release()
        except:
            pass

    def get_current_frame_index(self):
        return self._current_frame_index

    def get_time_text(self):
        cur_sec = self.get_current_frame_index() / self._fps
        return f"{self.get_time_formatted(cur_sec)}"

    @staticmethod
    def get_time_formatted(seconds):
        s, ms = divmod(seconds * 1000, 1000)
        if s < 3600:
            return '{}.{}'.format(time.strftime('%M:%S', time.gmtime(s)), "{0:02d}".format(int(ms / 10)))
        else:
            return '{}.{}'.format(time.strftime('%H:%M:%S', time.gmtime(s)), "{0:02d}".format(int(ms / 10)))

    @staticmethod
    def _find_video_capture():
        index = -1
        cap = cv2.VideoCapture(index)
        r, fr = cap.read()
        while fr is None:
            index += 1
            if index > 100:
                raise Exception('Cannot capture camera video')
            try:
                cap = cv2.VideoCapture(index)
                r, fr = cap.read()
            except:
                fr = None
        return cap
