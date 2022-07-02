import numpy
import cv2
import threading
import time


_image=None
_RUNNING1=True
_LOCK = threading.Lock()

def capture() -> None:
    global _image,_RUNNING1
    
    try:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        try_cap_time = 0
        while _RUNNING1:
            if cap.isOpened():
                with _LOCK:
                    ret, _image = cap.read()
            else:
                print('Error: opencv open camera failed')
                break
            inference_image = cv2.cvtColor(src=_image, code=cv2.COLOR_BGR2BGR565)
            
    except KeyboardInterrupt:
        _RUNNING1=False
    cap.release()
        

thrd_capture = threading.Thread(target=capture)
thrd_capture.start()

cv2.namedWindow('Cam', cv2.WND_PROP_ASPECT_RATIO or cv2.WINDOW_GUI_EXPANDED)
cv2.setWindowProperty('Cam', cv2.WND_PROP_ASPECT_RATIO, cv2.WND_PROP_ASPECT_RATIO)
while True:
    with _LOCK:
        if None is not _image:
            cv2.imshow('Cam', _image)
    if (27 == cv2.waitKey(10)) or (not _RUNNING1):
        cv2.destroyAllWindows()
        thrd_capture.join()
        thrd_display.join()
        break

