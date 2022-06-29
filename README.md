# 樹梅派自走車程序

```
maintainer:　junew@aiacademy.tw
```

## 簡介
與Arduino相比，樹梅派的程式設計更為彈性。在這裡我們分成4個程式碼進行教學分別是：
1. `car.py`: 定義了一個`car_control`的class，用來建立一個車子的物件，裡面包含了簡單的動作
2. `hcsr04.py`: 超音波模組，裡面定義了一個`get_distance`方法用來透過超音波模組取得距離
3. `car_control.py`: 呼叫`car`、`hcsr04`兩個模組，進行自走車控制應用。透過Ctrl+c可以關閉程序，自走車會停止運轉
4. `stop_car.py`: 因為沒有os做管理，當使用Ctrl+c關閉`car_control`的時候可能會因為`hcsr04.py`導致程序即使關閉，自走車卻持續運轉，這時候可以呼叫這個程序強迫自走車停止

## 前置:
1. 燒錄樹梅派rasbian到sd卡內，並安裝到樹梅派上
2. 安裝與使用vnc

## 流程:
在自己的電腦上使用VNC連接到樹梅派。然後打開terminal，用`git clone`把程式碼的repo拉下來

```
git clone https://gitlab.aiacademy.tw/junew/EdgeAI_code_temp.git
```

完成下載後，打開terminal，進入`RPI`資料夾
```
cd ./EdgeAI_code_temp/RPI
```

想要直接讓車子自走，可以啟動控制程序
```
python car_control.py
```
這時候可以在vnc上關閉terminal(Ctrl+c)，自走車就會停止運行
- 如果因為意外當機。重新開啟terminal，輸入`python stop_car.py`自走車就會停下了。