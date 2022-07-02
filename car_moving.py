from pynput.keyboard import Key,Listener
from car import CarController
from time import sleep

c = CarController()
action={
    "w":c.forward,
    "s":c.backward,
    "a":c.left,
    "d":c.right,
    Key.space:c.still,
    "q":c.close
}
last_key=" "

def on_press(key):
    if last_key==key:
        pass
    else:
        try:
            action[key]()
            last_key=key
        except:
            pass
    return True
def on_release(key):
    c.still()
    last_key=" "
    return False

while 1:
    listener=Listener(on_press=on_press,on_release=on_release)
    listener.start()
    listener.join()
    listener.stop()
        