import serial
import binascii
from time import sleep,time

initCmd = '56 00 26 00'      # 复位
takeCmd = '56 00 36 01 00'   # 拍照
clearCmd = '56 00 36 01 02'  # 清缓存
lenghtCmd = '56 00 34 01 00' # 读所拍照的长度,返回最后四位是XX和YY
dataCmd = '56 00 32 0C 00 0A 00 00 XX XX 00 00 YY YY ZZ ZZ'# 获取图片数据
# XX XX 起始地址 00 00 
# YY YY 第一个是高,第个是低
# ZZ ZZ 间隔时间, 00 0A
stopCmd = '56 00 36 01 03'   # 停止拍照
cutCmd = '56 00 31 05 01 01 12 04 XX'   # 压缩图片 XX:一般36, 00--FF 00最清晰 FF是255
sizeCmdA = '56 00 31 05 04 01 00 19 11' # 设置拍照图片大小,默认这个320*240
sizeCmdB = '56 00 31 05 04 01 00 19 00' # 设置拍照图片大小, 640 * 480
enterCmd = '56 00 3E 03 00 01 01'       # 进入省电模式
quitCmd = '56 00 3E 03 00 01 00'        # 退出省电模式
changeCmd = '56 00 24 03 01 XX XX'      # 修改波特率 0D A6是115200

# 生成16进制
def makeHex(str):
    return bytes.fromhex(str)

# 转为16进制查看
def changeHex(var):
    return str(binascii.b2a_hex(var))[2:-1]

# 字节集拼接
def mixed(data):
    ret = b''
    hlen = len(data)
    for i in range(hlen):
        ret = ret + data[i]
    return ret

# 接受
def recv(ser):
    return mixed(ser.readlines())



# 初始化
def rst(ser):
    ser.write(makeHex(initCmd))     # 初始化
    sleep(2.5)
    recv(ser)                       # 获取返回信息
    ser.write(makeHex(clearCmd))    # 清除缓存
    recv(ser)                       # 获取返回信息
    # ser.write(makeHex(sizeCmdB))    # 设置640 * 480
    # print(changeHex(recv(ser)))     # 获取返回信息
    ser.write(makeHex(cutCmd.replace('XX','36')))   # 初始化清晰度

# 拍照并写入文件
def savePhoto(ser,path):
    ser.write(makeHex(takeCmd))     # 拍照
    recv(ser)                       # 获取返回信息
    ser.write(makeHex(lenghtCmd))   # 获取图片大小
    lenghtData = changeHex(recv(ser))          # 获取返回信息
    l = lenghtData[-2:]             # 低位字节
    h = lenghtData[:-2][-2:]        # 高位字节
    print('总:',lenghtData)
    print("高:",h)
    print("低:",l)
    datac = dataCmd.replace('XX XX','00 00')
    datac = datac.replace('YY YY', str(h)+' '+str(l) )
    datac = datac.replace('ZZ ZZ','00 0A')
    ser.write(makeHex(datac))
    a = recv(ser)                   # 获取原数据
    b = changeHex(a)                # 转为16进制
    c = b[10:]
    c = c[:-10]
    f = open(path,'wb')
    f.write(binascii.unhexlify(c))  # 16进制转2进制写入
    f.close()
    ser.write(makeHex(stopCmd))     # 停止拍照
    recv(ser)                       # 获取返回信息
    print('ok!')

# 摄像头引脚向下拍出来是正的
try:
    ser = serial.Serial("COM3",115200,timeout=1)
    rst(ser)
    print('init success')
except:
    print('init error')


while True:
    name = input('save_file_name:')
    if name=='tst':
        rst()
    elif name=='quit':
        ser.close()
        exit()
    else:
        savePhoto(ser,name+str(time())+'.jpeg')