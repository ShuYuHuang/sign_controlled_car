import sys,termios,tty
from car import CarController
from time import sleep

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
c = CarController()
action={
    "w":c.forward,
    "s":c.backward,
    "a":c.left,
    "d":c.right,
    " ":c.still,
    "q":c.close
}
last_char=" "
while 1:
    char=getch()
    if char=="q":
        print('關閉程式 ')
        break
    try:
        if last_char!=char:
            action[char]()
            last_char=char
    except:
        pass
        