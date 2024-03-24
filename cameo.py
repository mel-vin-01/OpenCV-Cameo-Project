import cv2
import filters
from managers import WindowManager, CaptureManager
import depth


class Cameo(object):
    def __init__(self, windowName='Cameo', _shouldMirrorPreview=True):
        self._windowManager = WindowManager(windowName, self.onKeypress)
        self._captureManager = CaptureManager(
            capture=cv2.VideoCapture(0),
            previewWindowManager=self._windowManager,
            shouldMirrorPreview=_shouldMirrorPreview)
        self._pictureNumber: int = 0
        self._videoNumber: int = 0
        self._curveFilter = filters.BGRPortraCurveFilter()

    def run(self):
        """Run the main loop.
        :rtype: object
        """

        # print the key-operation
        print("Press space  to take a screenshot\n" +
              "      escape to quit\n" +
              "      tab    to start/stop recording a screencast\n")
        self._windowManager.createWindow()
        while self._windowManager.isWindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame

            # TODO: Filter the frame (Chapter3).
            filters.strokeEdges(frame, frame)
            self._curveFilter.apply(frame, frame)

            self._captureManager.exitFrame()
            self._windowManager.processEvents()

    def onKeypress(self, keycode):
        """ Handle a keypress

        space       ->    Take a screenshot.
        tab         ->    Start/stop recording a screencast.
        escape      ->    Quit.

        """
        if keycode == 32:  # space
            self._pictureNumber += 1
            print("Take a screenshot named screenshot" + str(self._pictureNumber) + ".png\n")

            self._captureManager.writeImage('screenshot' + str(self._pictureNumber) + ".png")
        elif keycode == 9:  # tab
            if not self._captureManager.isWritingVideo:
                self._videoNumber += 1
                print("Start recording a screencast...\n")

                self._captureManager.startWritingVideo('screencast' + str(self._videoNumber) + ".mp4")
            else:
                self._captureManager.stopWritingVideo()
                print("Stop recording a screencast... \n" +
                      "screencast" + str(self._videoNumber) + ".mp4 saved.\n")
        elif keycode == 27:  # escape
            print("Quit.\n")
            self._windowManager.destroyWindow()


class CameoDepth(Cameo):

    def __init__(self, windowName='Cameo', _shouldMirrorPreview=True):
        self._windowManager = WindowManager(windowName, self.onKeypress)
        device = cv2.CAP_OPENNI2_ASUS
        self._captureManager = CaptureManager(cv2.VideoCapture(device), self._windowManager, True)
        self._curveFilter = filters.BGRPortraCurveFilter()

    def run(self):
        """Run the main loop."""
        self._windowManager.createWindow()
        while self._windowManager.isWindowCreated:
            self._captureManager.enterFrame()
            self._captureManager.channel = cv2.CAP_OPENNI_DISPARITY_MAP
            disparityMap = self._captureManager.frame
            self._captureManager.channel = cv2.CAP_OPENNI_VALID_DEPTH_MASK
            validDepthMask = self._captureManager.frame
            self._captureManager.channel = cv2.CAP_OPENNI_BGR_IMAGE
            frame = self._captureManager.frame
            if frame is None:
                # failed to capture BGR frame
                # try to capture an infrared frame instead
                self._captureManager.channel = cv2.CAP_OPENNI_IR_IMAGE

            if frame is not None:

                # Make everything except the median layer black
                mask = depth.createMedianMask(disparityMap, validDepthMask)
                frame[mask == 0] = 0

                if self._captureManager.channel == cv2.CAP_OPENNI_BGR_IMAGE:
                    # A BGR frame was captured
                    # Apply filters to it.
                    filters.strokeEdges(frame, frame)
                    self._curveFilter.apply(frame, frame)

            self._captureManager.exitFrame()
            self._windowManager.processEvents()
