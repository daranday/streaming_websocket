import websocket
try:
    import thread
except ImportError:
    import _thread as thread

import sys
import time
from cStringIO import StringIO

import cv2
import gflags
import numpy as np
from imutils.video import WebcamVideoStream
from PIL import Image

from imutils.video import FPS
import base64


gflags.DEFINE_integer('port', 9001, 'port')
gflags.DEFINE_string('host', '0.0.0.0', 'hostname')
FLAGS = gflags.FLAGS


def close_windows():
    dummy = np.zeros(1)
    cv2.destroyAllWindows()
    cv2.waitKey(-1)
    cv2.imshow('dummy', dummy)


class ImageCaption(object):
    """docstring for ImageCaption"""

    HEIGHT = 30
    RED = (0, 0, 255)
    FONT = cv2.FONT_HERSHEY_SIMPLEX

    @classmethod
    def writerows(cls, img, lines):
        for i, line in enumerate(lines):
            pos = (5, 18 + cls.HEIGHT * i)
            cv2.putText(img, line, pos, cls.FONT, 0.6, cls.RED, 2)


class StreamingWebsocket(object):
    """docstring for StreamingWebsocket"""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.fps = FPS().start()

    @classmethod
    def load_base64_img(cls, base64_string):
        sbuf = StringIO()
        sbuf.write(base64.b64decode(base64_string))
        pimg = Image.open(sbuf)
        return np.array(pimg)[..., ::-1]

    def on_message(self, ws, message):
        resp_frame = self.load_base64_img(message).copy()
        # Display the resulting frame
        self.fps.update()
        self.fps.stop()
        ImageCaption.writerows(resp_frame, ['FPS: ' + str(self.fps.fps())])
        cv2.imshow('frame', resp_frame)
        k = chr(cv2.waitKey(1) & 0xFF)
        if k == 'q':
            exit(0)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            cap = WebcamVideoStream(src=0).start()
            self.fps.update()
            while(True):
                # Capture frame-by-frame
                frame = cap.read()
                ret, buf = cv2.imencode('.jpg', frame)
                frame_serialized = base64.b64encode(buf)
                ws.send(frame_serialized)
                time.sleep(0.1)

            # When everything done, release the capture
            self.fps.stop()
            cap.stop()
            close_windows()
        thread.start_new_thread(run, ())

    def run(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://{}:{}/".format(self.host, self.port),
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever()


if __name__ == '__main__':
    FLAGS(sys.argv)
    streamer = StreamingWebsocket(FLAGS.host, FLAGS.port)
    streamer.run()
