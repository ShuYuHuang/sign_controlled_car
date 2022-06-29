from car import CarController
from time import sleep

c = CarController()
action={
    0:c.forward,
    1:c.backward,
    2:c.left,
    3:c.right,
    4:c.still
}
try:
    while 1:
        cls=classifier()
        action[cls]()
        sleep(0.5)
        c.still()
except KeyboardInterrupt:
    c.still()
    print('關閉程式 ')