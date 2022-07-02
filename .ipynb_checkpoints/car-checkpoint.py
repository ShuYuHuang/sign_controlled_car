import RPi.GPIO as gpio
import time

###############################################################
# Genral Purpose Input/Output (GPIO) pin control
# 控制GPIO接腳，以便控制馬達前後轉動，形成前進/後退/左轉/右轉等動作
# Input:不用，我們把控制的接腳寫死
# Objects: 有四個物件控制四個接腳，共兩對前後控制，
#          每對接腳對一個輪子可以傳出: 前/後/停 三種指令
# Functions: 
# - forward(): 前進
# - backward(): 後退
# - left(): 左旋轉
# - right(): 右旋轉
# - still(): 停


class CarController():
    def __init__(self,duty_cycle=30):
        # 使用BCM模式，等會址定的接腳數字是根據GPIO輸出編號，而不是相對位置
        # 編號對應詳見https://ithelp.ithome.com.tw/articles/10237152
        gpio.setmode(gpio.BCM) 
        gpio.setwarnings(False) #把warning關掉，不然很吵
                
        # 指定a1,b1,a2,b2為global物件
        global a1,b1,a2,b2
        # 設定用到的接腳為output
        gpio.setup(23,gpio.OUT) 
        gpio.setup(24,gpio.OUT)
        gpio.setup(5,gpio.OUT)
        gpio.setup(6,gpio.OUT)
        
        # 開啟一個電脈衝控制物件a1(我們用馬達控制晶片接腳名稱來命名)，控制接腳23、給定脈衝頻率30
        # 後面會針對四個接腳訊號控制的物件做啟動，格式都一樣我就說明一個
        a1 = gpio.PWM(23, 30)# 設定電脈衝控制物件接腳、脈衝頻率
        
        # 開啟一個電脈衝控制物件b1，控制接腳24、給定脈衝頻率30
        b1 = gpio.PWM(24, 30)
        
        # 開啟一個電脈衝控制物件a2，控制接腳5、給定脈衝頻率30
        a2 = gpio.PWM(5, 30)
        
        # 開啟一個電脈衝控制物件b2，控制接腳6、給定脈衝頻率30
        b2 = gpio.PWM(6, 30)
        
        self.duty_cycle=duty_cycle # 紀錄參數給用，預設30
        self.last_move=4
    def __version__(self):
        print('beta03')
    # 以下為一些控制程式，可參考: https://wp.huangshiyang.com/pwm%E4%BD%BF%E7%94%A8-rpi-gpio-%E6%A8%A1%E5%9D%97%E7%9A%84%E8%84%89%E5%AE%BD%E8%B0%83%E5%88%B6
    def forward(self):
        if self.last_move!=0:
            # 前進，兩個輪子輸出前進的脈衝波
            a1.start(0)
            b1.start(self.duty_cycle) # 數字從0~100 代表0~100% duty cycle，是有脈衝的時間佔週期的多少
            a2.start(self.duty_cycle) # 同個號碼(1or2)的a跟b的給電要分開(一個前進一個後退)不能一起給
            b2.start(0)  # 有脈衝就有給電，0就是完全不給電就不使用
            self.last_move=0
    def backward(self):
        if self.last_move!=1:
            # 後退，兩個輪子輸出後退的脈衝波
            a1.start(self.duty_cycle)
            b1.start(0)
            a2.start(0)
            b2.start(self.duty_cycle)
            self.last_move=1
    def left(self):
        if self.last_move!=2:
            # 左旋轉，右輪往前，左輪往後
            a1.start(self.duty_cycle)
            b1.start(0)
            a2.start(self.duty_cycle)
            b2.start(0)
            self.last_move=2
    def right(self):
        if self.last_move!=3:
            # 左旋轉，右輪往前，左輪往後
            a1.start(0)
            b1.start(self.duty_cycle)
            a2.start(0)
            b2.start(self.duty_cycle)
            self.last_move=3

    def still(self):
        if self.last_move!=4:
            # 暫停，輪子不動
            a1.start(0)
            b1.start(0)
            a2.start(0)
            b2.start(0)
            self.last_move=4
    def close(self):
        self.last_move=5
        # 把所有控制元件停住
        a1.stop()
        b1.stop()
        a2.stop()
        b2.stop()
        gpio.cleanup() # 把腳位全部設回input(接收而不發訊)

if __name__ == '__main__':
    c = CarController()
    c.left()
    time.sleep(1)
    c.right()
    time.sleep(1)
    c.still()
    time.sleep(1)
    c.right()
    time.sleep(1)
    c.left()
    time.sleep(1)
    c.close()
    
    
    
###############################################################
# Version:
# - beta01: 基本物件+前進/左轉/停 by 王柏鈞(June)
# - beta02: 註解+功能改為: 前進/後退/左旋轉/右旋轉/停
# - beta03: 功能改為: 前進/後退/左旋轉/右旋轉/暫停/關閉，並修正bug
