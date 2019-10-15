from flask import Flask, request
from flask_cors import *
import time, threading

app = Flask(__name__)
DAU = []
DRR = []
DRR7 = []
AET = []
days = []  # 保存日志中读出的每日的数据
lock = threading.Lock()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/dayUpload', methods=['POST'])
@cross_origin()
def dayUpload():
    f = request.files['file']
    f.save('newdayupload.txt')
    return 'upload success'


@app.route('/upload', methods=['POST'])
@cross_origin()
def upload():
    f = request.files['file']

    f.save('newUpload.txt')
    return 'file uploaded success'


@app.route('/calData', methods=['POST'])
@cross_origin()
def calData():  #30天日志的提交方法
    print("calData")
    calDays()
    print(days.__len__())
    # 开启四条计算线程
    cDAU = calDAUThread()
    cDRR = calDRRThread()
    cDRR7 = calDRR7Thread()
    cAET = calAETThread()
    cDAU.start()
    cDRR.start()
    cDRR7.start()
    cAET.start()
    return 'calData start success'

@app.route('/calDayData', methods=['POST'])
@cross_origin()
def calData():  #每天日志的提交方法
    print("calDayData")
    #开启计算日志线程
    daycal=Days()
    daycal.start()
    # 开启四条计算线程
    cDAU = calDAUThread()
    cDRR = calDRRThread()
    cDRR7 = calDRR7Thread()
    cAET = calAETThread()
    cDAU.start()
    cDRR.start()
    cDRR7.start()
    cAET.start()
    return 'calData start success'



@app.route('/selectDataLong', methods=['POST'])
@cross_origin()
def selectDataLong():
    sum = 30 * 5
    value = len(DAU) + len(DRR) + len(DRR7) + len(AET) + len(days)
    print(sum)
    print(value)
    return 'sum=' + str(sum) + '&value=' + str(value)


@app.route('/selectData', methods=['POST'])
@cross_origin()
def selectData():
    print('selectData')
    tem = []
    for i in days:
        tem.append(days.index(i) + 1)
    res = {'DAU': DAU, 'DRR': DRR, 'DRR7': DRR7, 'AET': AET, 'days': tem}
    return res


def calDays():
    with open('newUpload.txt', 'r') as fp:
        l = fp.readlines()
    firstDay = time.strptime(l[0].split(' ')[0], "%Y/%m/%d")
    lastDay = time.strptime(l[-1].split(' ')[0], "%Y/%m/%d")
    for i in range(30):
        t = time.mktime(firstDay) + i * 86400
        t = time.localtime(t)
        day = filter(lambda x: x.split(' ')[0] == time.strftime("%Y/%m/%d", t), l)
        days.append(list(day))
    return days


class Days(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        oldread = ''
        while (True):
            lock.acquire()
            with open('newdayupload.txt', 'r') as fp:
                read = fp.readlines()
            if read == oldread:
                pass
            else:
                days.append(read)
                oldread = read
            lock.release()


class calDAUThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        dataNumber = 0
        while (True):
            lock.acquire()
            if dataNumber >= len(days):
                lock.release()
                break
            day = days[dataNumber]
            day = filter(lambda x: x.split(' ')[2] == 'login' and
                                   x.split(' ')[4].__contains__('success'), day)
            res = len(set(map(lambda x: x.split(' ')[3], day)))
            DAU.append(res)
            dataNumber += 1
            lock.release()
            print('DAU' + str(dataNumber))
            time.sleep(0.01)
        print('DAU   success')
        print(DAU)


class calDRRThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        dataNumber = 0
        while (True):
            if dataNumber >= len(days):
                dataNumber += 1
                break
            lock.acquire()
            day = days[dataNumber]
            if day == days[-1]:  # 最后一日的次留记为0
                DRR.append(0.0)
                dataNumber += 1
                lock.release()
                continue
            registeredWithLogin = 0
            registered = list(filter(lambda x: x.split(' ')[2] == 'registered', day))
            login = set(map(lambda x: x.split(' ')[3],
                            filter(lambda x: x.split(' ')[2] == 'login' and
                                             x.split(' ')[4].__contains__('success'),
                                   days[days.index(day) + 1])))
            for i in registered:
                if login.__contains__(i.split(' ')[3]):
                    registeredWithLogin += 1
            res = registeredWithLogin / registered.__len__()
            DRR.append('{:.4f}'.format(res))
            dataNumber += 1
            lock.release()
            print('DRR' + str(dataNumber))
            time.sleep(0.01)
        print('DRR   success')
        print(DRR)


class calDRR7Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        dataNumber = 0
        while (True):
            if dataNumber >= len(days):
                break
            lock.acquire()
            day = days[dataNumber]
            if days.index(day) >= 23:  # 最后7日的7日留存记为0
                DRR7.append(0.0)
                dataNumber += 1
                lock.release()
                continue
            registeredWithLogin = 0
            registered = list(filter(lambda x: x.split(' ')[2] == 'registered', day))
            login = set(map(lambda x: x.split(' ')[3],
                            filter(lambda x: x.split(' ')[2] == 'login' and
                                             x.split(' ')[4].__contains__('success'),
                                   days[days.index(day) + 7])))
            for i in registered:
                if login.__contains__(i.split(' ')[3]):
                    registeredWithLogin += 1
            res = registeredWithLogin / registered.__len__()
            DRR7.append('{:.4f}'.format(res))
            dataNumber += 1
            print('DRR7' + str(dataNumber))
            lock.release()
            time.sleep(0.01)
        print('DRR7   success')
        print(DRR7)


class calAETThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        dataNumber = 0
        while (True):
            if dataNumber >= len(days):
                break
            lock.acquire()
            day = days[dataNumber]
            sumgames = 0
            sumgametime = 0.0
            createRoom = list(filter(lambda x: x.split(' ')[2] == 'createRoom', day))
            closeRoom = list(filter(lambda x: x.split(" ")[2] == 'closeRoom', day))
            for i in createRoom:
                for j in closeRoom:
                    if i.split(' ')[3] == j.split(' ')[3]:
                        starttime = time.mktime(time.strptime(
                            i.split(' ')[0] + ' ' + i.split(' ')[1],
                            "%Y/%m/%d %H:%M:%S"))
                        endtime = time.mktime(time.strptime(
                            j.split(' ')[0] + ' ' + j.split(' ')[1],
                            "%Y/%m/%d %H:%M:%S"))
                        gametime = endtime - starttime
                        sumgames += 1
                        sumgametime += gametime
                        closeRoom.remove(j)  # 减少closeRoom的长度提升下效率
                        break
            res = (sumgametime / 3600) / sumgames
            AET.append('{:.4f}'.format(res))
            dataNumber += 1
            print('AET' + str(dataNumber))
            lock.release()
            time.sleep(0.01)
        print('AET   success')
        print(AET)


if __name__ == '__main__':
    app.run()
