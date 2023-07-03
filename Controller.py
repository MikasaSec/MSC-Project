#sudo python3 Controller.py
import threading
import Assembly
import Monitor
import Perception
import Detection
import time

def process1():
    perception = Perception.Perception()
    time.sleep(5)
    loc = perception.locationDetect()
    assembly = Assembly.Assembly()
    mode = assembly.Assemble(loc)
    detection = Detection.Detection()
    detection.Detect(mode)

def process2():
    monitor = Monitor.Monitor()



if __name__ == '__main__':
    t1 = threading.Thread(target=process1)
    t2 = threading.Thread(target=process2)

    t1.start()
    t2.start()

    while True:
        if t2.is_alive():
            continue
        else:
            t1.join(timeout=0)  # 终止 process1
            t1 = threading.Thread(target=process1)  # 创建新的 process1
            time.sleep(5)
            t1.start()  # 启动新的 process1
            t2 = threading.Thread(target=process2)
            t2.start()



