import os
import time

import cv2

if __package__ is None or __package__ == '':
    from video_source import VideoSource
else:
    from .video_source import VideoSource


class FileVideoSource(VideoSource):
    def __init__(self, file_path):
        super(FileVideoSource, self).__init__()
        self.__capture: cv2.VideoCapture = None
        self._fps = 0
        self.__video_path = file_path
        if self.__video_path is None:
            raise ValueError("Video file path is empty")

        if os.path.isfile(self.__video_path) is False:
            raise ValueError("Video file is not exist : %s", self.__video_path)
        self._set_capture()

    def _set_capture(self):
        if os.path.isfile(self.__video_path) is False:
            raise ValueError("Video file is not exist")
        self.__capture = cv2.VideoCapture(self.__video_path)
        self._fps = self.__capture.get(cv2.CAP_PROP_FPS)
        self.frame_count = self.__capture.get(cv2.CAP_PROP_FRAME_COUNT)
        if self.frame_count > 0:
            self.time_text_suffix = f" / {self.get_time_formatted(self.frame_count / self._fps)}"
        else:
            self.time_text_suffix = f" / ???"

    def fps(self):
        return self._fps

    def reset(self):
        self.stop()
        self._set_capture()

    # returns ok, frame
    def next(self, skip=0):
        if self.__capture.isOpened():
            if skip > 0:
                if skip > 15:
                    return self.goto(self.get_current_frame_index() + skip)
                else:
                    for i in range(skip):
                        ok, frame = self.__capture.read()
                    return ok, frame
            else:
                return self.__capture.read()
        else:
            return False, None

    # returns ok, frame
    def previous(self, skip=0):
        if self.__capture.isOpened():
            if skip > 0:
                return self.goto(self.get_current_frame_index() - skip)
            else:
                next_frame = self.__capture.get(cv2.CAP_PROP_POS_FRAMES)
                current_frame = next_frame - 1
                previous_frame = current_frame - 1
                return self.goto(previous_frame)
        else:
            return False, None

    # returns ok, frame
    def goto(self, frame_index):
        if frame_index >= 0 and self.__capture.isOpened():
            self.__capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            return self.__capture.read()
        else:
            return False, None

    def stop(self):
        try:
            self.__capture.release()
            cv2.destroyAllWindows()
            self.__capture = None
        except:
            pass

    def get_current_frame_index(self):
        return int(self.__capture.get(cv2.CAP_PROP_POS_FRAMES) - 1)

    def get_time_text(self):
        cur_sec = self.get_current_frame_index() / self._fps
        return f"{self.get_time_formatted(cur_sec)}{self.time_text_suffix}"

    @staticmethod
    def get_time_formatted(seconds):
        s, ms = divmod(seconds * 1000, 1000)
        if s < 3600:
            return '{}.{}'.format(time.strftime('%M:%S', time.gmtime(s)), "{0:02d}".format(int(ms / 10)))
        else:
            return '{}.{}'.format(time.strftime('%H:%M:%S', time.gmtime(s)), "{0:02d}".format(int(ms / 10)))
