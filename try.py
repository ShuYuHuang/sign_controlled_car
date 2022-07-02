from pynput.keyboard import Key,KeyCode,Listener
def on_press(key):
    
    print(key,KeyCode(8))
    return True
listener=Listener(on_press=on_press)
listener.start()
listener.join()