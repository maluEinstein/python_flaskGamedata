import time, threading

lock = threading.Lock()
DAU = []
DRR = []
DRR7 = []
AET = []
days = []
onedaydata = ''




class DRR7(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while (True):
            lock.acquire()
            if DRR7.__len__()<days.__len__():
                temdays=days[DRR7.__len__()-1:]
                for i in temdays:
                    pass



