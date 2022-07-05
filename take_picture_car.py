from pynput.keyboard import Key,Listener
import threading
import time
from car import CarController
import cv2

_image=None
class CamCar:
    def __init__(self):
        self.state=0
        self.t=0
        self.n=0
        self._LOCK=threading.Lock()
        self.c=CarController()
        self.action_mapping={
            "w":self.c.forward,
            "s":self.c.backward,
            "a":self.c.left,
            "d":self.c.right,
            "e":self.take_photo,
            "q":self.c.close
        }
    def take_photo(self):
        global _image
        with self._LOCK:
            cv2.imwrite(f"pictures/{self.n}.jpg",_image)
            cv2.putText(img=_image,
                        text=f'Saved as: pictures/{self.n}.jpg',
                        org=(10, 30),
                        fontFace=cv2.FONT_HERSHEY_DUPLEX,
                        fontScale=0.5,
                        color=(200, 200, 200),
                        thickness=1,
                        lineType=cv2.LINE_AA)
        self.n+=1
    def on_press(self,key):
        if key==Key.esc:
            self.c.close()
            print("Bye")
            self.state=9
            return True
        try:
            self.action_mapping[key.char]()
        except:
            pass
        return True
        
    def on_release(self,key):
        if key==Key.esc:
            return False
        if self.state==0:
            self.state=1
        self.t=time.time()
        return False

    def on_true_release(self) -> None:
        while self.state!=9:
            if self.state==1:
                elapsed=time.time()-self.t
                if elapsed>0.6:
                    #print(elapsed,"released")
                    self.c.still()
                    self.state=0
    def capture(self) -> None:
        global _image

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 224)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 224)
        while self.state!=9:
            #with self._LOCK:
            if cap.isOpened():
                ret, _image = cap.read()
            else:
                print('Error: opencv open camera failed')
                break
        cap.release()
    def listen(self) ->None:
        while self.state!=9:
            listener=Listener(on_press=self.on_press,
                              on_release=self.on_release,
                              suppress=False)
            listener.start()
            listener.join()
            listener.stop()
    def go(self):
        cv2.namedWindow('Cam', cv2.WND_PROP_ASPECT_RATIO or cv2.WINDOW_GUI_EXPANDED)
        cv2.setWindowProperty('Cam', cv2.WND_PROP_ASPECT_RATIO, cv2.WND_PROP_ASPECT_RATIO)
        thrd_timing = threading.Thread(target=self.on_true_release)
        thrd_listen = threading.Thread(target=self.listen)
        thrd_capture = threading.Thread(target=self.capture)
        thrd_timing.start()
        thrd_listen.start()
        thrd_capture.start()
        while True:
            #with self._LOCK:
            if _image is not None:
                cv2.imshow('Cam', _image)
            if (27 == cv2.waitKey(10)) or (self.state==9):
                cv2.destroyAllWindows()
                thrd_timing.join()
                thrd_listen.join()
                thrd_capture.join()
                _RUNNING1=False
                break
if __name__ == '__main__':
    print('''Control the car and take pictures:
        w-> front
        s-> back
        a-> left turn
        d-> right turn
        e-> take picture to "picture/xxx.jpg"
        esc-> quit
    ''')
    car=CamCar()
    car.go()
