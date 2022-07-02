from pynput.keyboard import Key,Listener
import threading
import time
from car import CarController
import cv2
c = CarController()
mapping={
    "w":c.forward,
    "s":c.backward,
    "a":c.left,
    "d":c.right,
    "q":c.close
}


class Args:
    state=0
    t=0
args=Args()

def on_press(key):
    global last_key
    if key==Key.esc:
        c.close()
        print("Bye")
        args.state=9
        return True
    try:
        mapping[key.char]()
    except:
        pass
    return True
        
def on_release(key):
    if key==Key.esc:
        return False
    if args.state==0:
        args.state=1
    args.t=time.time()
    return False

def on_true_release() -> None:
    while 1:
        if args.state==9:
            break
        if args.state==1:
            elapsed=time.time()-args.t
            if elapsed>0.6:
                print(elapsed,"released")
                c.still()
                args.state=0
        
            

timing_thread = threading.Thread(target=on_true_release)
timing_thread.start()
cv2.namedWindow('Cam', cv2.WND_PROP_ASPECT_RATIO or cv2.WINDOW_GUI_EXPANDED)
cv2.setWindowProperty('Cam', cv2.WND_PROP_ASPECT_RATIO, cv2.WND_PROP_ASPECT_RATIO)

while 1:
    listener=Listener(on_press=on_press,on_release=on_release,suppress=True)
    listener.start()
    listener.join()
    listener.stop()
    if args.state==9:
        break
timing_thread.join()
