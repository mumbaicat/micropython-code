import socket
import network
import machine
from machine import Pin

# 连接同一个wifi里
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect('wifi','password')
print(sta.ifconfig())



# 连接遥控服务器
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client.connect(socket.getaddrinfo('192.168.31.98',1272)[0][-1])


b1 = machine.Pin(12,Pin.PULL_UP,value=0)
b2 = machine.Pin(13,Pin.PULL_UP,value=0)
b3 = machine.Pin(14,Pin.PULL_UP,value=0)
b4 = machine.Pin(15,Pin.PULL_UP,value=0)


count = 0
while True:
  data = ''
  if b1.value() ==1:
    data = data + 'a|'
  if b2.value() == 1:
    data = data + 'b|'
  if b3.value() == 1:
    data = data + 'c|'
  if b4.value() == 1:
    data = data + 'd|'
  
  if data != '':
    count = count +1
    client.send(data.encode('utf-8'))
    print(str(count)+':'+data)
  time.sleep(0.1)


print('运行完毕...')