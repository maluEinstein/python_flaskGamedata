import random
import time


class robotPlayer:
    def __init__(self, userId, onT, offT, gameT, ft):
        self.userId = userId
        self.online = False
        self.name = 'None'
        self.loginT = 0  # 上次登录时间
        self.logoutT = 0  # 上次离线时间
        self.onT = onT  # 计划在线时长
        self.offT = offT  # 计划离线时长
        self.gameT = gameT  # 计划游戏时长（在房间中待的时间）
        self.createRoomTime = 0  # 上次开房时间
        self.inRoom = False
        self.ft = ft
        self.selfTime = 0  # 当前时间
        self.updatetime = 0

    def setSelfTime(self, t):
        # print(int(self.setSelfTime+t))
        self.selfTime = int(self.selfTime + t)
        return self.selfTime

    def showTime(self, t):
        return str(time.strftime("%Y/%""m/%d %H:%M:%S", time.localtime(t)))

    def createRoom(self):
        self.inRoom = True
        self.createRoomTime = self.selfTime
        s = self.showTime(self.createRoomTime) + ' createRoom ' + str(self.userId) + ' success' + '\n'
        with open('e:/12.txt', 'a') as fp:
            fp.writelines(s)

    def login(self):
        s = ''
        if random.uniform(0, 1) < self.ft:  # 登录失败
            if random.uniform(0, 1) < 0.9:  # 登录失败之后9成的玩家选择下一秒再次尝试登录
                s = self.showTime(self.selfTime) + ' login ' + str(self.userId) + ' fail' + '\n'
            else:  # 一成的玩家选择过一段时间再来
                s = self.showTime(self.selfTime) + ' login ' + str(self.userId) + ' fail' + '\n'
                self.logoutT = self.selfTime  # 状态保持离线，吧离线时间置为现在
        else:
            self.online = True
            self.loginT = self.selfTime
            self.onT = random.randint(self.onT, self.onT * 2)
            s = self.showTime(self.loginT) + ' login ' + str(self.userId) + ' success' + '\n'
        with open('e:/12.txt', 'a') as fp:
            fp.writelines(s)

    def logout(self):
        self.online = False
        self.logoutT = self.selfTime
        self.offT = random.randint(self.offT, int(self.offT * 1.5))
        s = self.showTime(self.logoutT) + ' logout ' + str(self.userId) + ' success' + '\n'
        if self.inRoom:
            self.inRoom = False
            s += self.showTime(self.logoutT) + ' closeRoom ' + str(self.userId) + ' success' + '\n'
        with open('e:/12.txt', 'a') as fp:
            fp.writelines(s)

    def update(self, t):
        self.selfTime = self.setSelfTime(t)
        if self.name != 'None':
            if self.online:
                if (self.selfTime - self.loginT) >= self.onT:
                    self.logout()
                else:
                    if self.inRoom:
                        if self.selfTime - self.createRoomTime >= self.gameT:
                            self.inRoom = False
                            s = self.showTime(self.selfTime) + ' closeRoom ' + str(self.userId) + ' success' + '\n'
                            with open('e:/12.txt', 'a') as fp:
                                fp.writelines(s)
                    else:
                        if random.uniform(0, 1) < 0.3:
                            self.createRoom()
            else:
                if (self.selfTime - self.logoutT) >= self.offT:
                    self.login()
        else:
            self.name = 'have registered'
            s = self.showTime(self.selfTime) + ' registered ' + str(self.userId) + ' success' + '\n'
            with open('e:/12.txt', 'a') as fp:
                fp.writelines(s)
            # return之后执行?有没有可能


class TimerData:
    def __init__(self):
        self.handle = 0
        self.callBack = None
        self.timeout = -1
        self.lastTirg = 0


class MyTimer:
    def __init__(self):
        self.genhandle = 0
        self.timerlist = []

    def setTimer(self, callback, timeout):
        self.genhandle += 1
        handle = self.genhandle
        td = TimerData()
        td.callBack = callback
        td.timeout = timeout
        td.handle = handle
        self.timerlist.append(td)

    def clearTimer(self, handle):
        for d in self.timerlist:
            if d.handle == handle:
                self.timerlist.remove(d)
                break

    def updata(self, t):
        for d in self.timerlist:
            if d.timeout > 0 and t >= (d.lastTirg + d.timeout):
                d.lastTirg = t
                d.callBack(t)


def createUser():
    # s='RB'+
    x = random.randint(3600 * 2, 3600 * 4)  # 初始计划在线时长
    y = random.randint(3600 * 4, 3600 * 8)  # 初始计划离线时长
    r = robotPlayer(s, x, y, 0.5)
    r.setSelfTime(t)
    userList.append(r)


path = 'e:/12.txt'
starttime = time.strptime("2019/09/11 00:00:00", "%Y/%m/%d %H:%M:%S")
startstamp = time.mktime(starttime)
userList = []
t = startstamp
end = startstamp + 3600 * 24 * 30
res = ''
timer_timeout = 720
timer_lasttrig = startstamp - timer_timeout
num = 0
print('begin')
n = 0
while t < end:
    if t >= (timer_timeout + timer_lasttrig):  # 时间到了新增用户
        s = 'RB' + "{:0>5d}".format(num)
        num = num + 1
        x = random.randint(3600 * 2, 3600 * 4)  # 初始计划在线时长
        y = random.randint(3600 * 4, 3600 * 8)  # 初始计划离线时长
        z = random.randint(4400 * 1, 3600 * 4)  # 计划游戏时长
        r = robotPlayer(s, x, y, z, 0.2)
        r.setSelfTime(t)
        userList.append(r)
        timer_lasttrig = t
    if t % (3600 * 10) == 0:  # 每10个小时计划删一次用户
        for i in userList[::-1]:
            if i.online:
                continue
            if random.uniform(0, 1) < 0.35:
                userList.remove(i)
    for i in userList:
        i.update(1)
    t = t + 1
    print(num)
print('end')
# print(calDAU(res))
