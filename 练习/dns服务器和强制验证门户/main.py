import socket
import network
import time
import machine
from machine import Pin
from machine import UART

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="esp8266-cp",authmode=1) # , password="12345678", authmode=4 authmode=1 == no pass
p = Pin(2,Pin.OUT,value=1)
u = UART(0,115200)

global ip
global udps
global addr
global counter
global data
global s

shutdown = False

def blink(times=2):
    global p
    for i in range(times):
        p.value(0)
        time.sleep(0.2)
        p.value(1)
        time.sleep(0.2)

CONTENT = b"""\
HTTP/1.0 200 OK

<!doctype html>
<html>
    <head>
        <title>广告</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta charset="utf8">
    </head>
    <body>
        广告位常年招租 [led]
        <img src='data:image/gif;base64,R0lGODlhdQAmAKIAAOYyL+rU4llg6Jmd8e92dCky4eEGAv///yH5BAAAAAAALAAAAAB1ACYAAAP/eLrc/jC2IEoZMATJu/9gyFVWIUyksIls677LUJbrEcxWDe98f+CWk4I0w/iOSNANKJQBC8mo9LEEDp8F3XR7rOIU2Cx3jHwKsUKyWqRhEEvGN3xN91BoCq8l9tTW/244Rk4mOkBGgIl8VjF+d4V5A5KKf3IWiCCEOZRraGxPnGqeIZpzoVyjDBptDpYmp1yumI9BWq5QUQS6fn+lm3lYmLdSBsW8xcjJBgAABLwfAMhXRQt6ODWuJ8rb3AYK0d3h4OHIBC7jC0TCYb/ZB+Th3/Dc4/PmLOgSvkwK+xjMAAEmCwhQnrc8rFSxGkiwnoFnEnTp0mdqlJw0DgIggwgu/08xABM+KkhGJdm9JJqMhGkyQIAATA3HxVwATuO8jyQfECiXJyYzZwzyOSilcqWEmzkP1ES6LGmDcStshjspNJAgMOwwNmBajGZXGyJVhU22quxOaR7hrahqQ52DC1jh/nj1AG0Eux3BLgu59x3SkxHO9mVLhJfcirUc2IWA96vUbvf+QkNbldCgIGCKHi6h1e/Bu1+VOiYHYAVTwBHyCfWyocoZzZovbf3ok1njzx/IltUg+GG13twMfta0gdDruLH3MOD6uaPDcI8hCAZp4/k24elmtOacGXlcPAuYe/VmnVt0ncioTyeYU+ibQRWOHyCRXEz40BDyivYWYBzQAIbTbeBUNTIZRF1QlNlVimGdfffLSPg9oJ9+vVV4H23smWSgFqrZZc0AWiTWACMXcjAhfgAqgxpXKwDXDXbZsSPjVcth6NNtZj3nzCpM1dDfPDACM+OQ9l2I1HiPlfNceentMoGLygQp5Eq3aKfYaUgOdBIB9RyYSEsmvASiFgG0RMRLEK2RAAA7' />
        <script>

        </script>
    </body>
</html>
"""

class DNSQuery:

  # 接收DNS udp报文进行处理
  def __init__(self, data):
    self.data=data
    self.dominio=''  # 原地址

    # print("Reading datagram data...")
    m = data[2] # ord(data[2])
    tipo = (m >> 3) & 15   # Opcode bits
    if tipo == 0:                     # Standard query
      ini=12
      lon=data[ini] # ord(data[ini])
      while lon != 0:
        self.dominio+=data[ini+1:ini+lon+1].decode("utf-8") +'.'
        ini+=lon+1
        lon=data[ini] #ord(data[ini])

  # 转发到ip
  def respuesta(self, ip):
    packet=b''
    # print("Resposta {} == {}".format(self.dominio, ip))
    if self.dominio:
      packet+=self.data[:2] + b"\x81\x80"
      packet+=self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'   # Questions and Answers Counts
      packet+=self.data[12:]                                         # Original Domain Name Question
      packet+= b'\xc0\x0c'                                             # Pointer to domain name
      packet+= b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
      packet+=bytes(map(int,ip.split('.'))) # 4 bytes of IP
    return packet

def reconfig():
    global ap
    global ip
    global udps
    global addr
    global counter
    global data
    global s

    try:
        s.close()
        udps.close()
    except:
        print('close')

    # DNS Server DNS服务配置 udp 53端口
    ip=ap.ifconfig()[0]
    print('DNS Server: dom.query. 60 IN A {:s}'.format(ip))

    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.setblocking(False)
    udps.bind(('',53))
    
    # Web Server  WEB服务器 tcp 80端口
    s = socket.socket()
    ai = socket.getaddrinfo(ip, 80)
    # print("Web Server: Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(100)
    s.settimeout(2)
    print("Web Server: Listening http://{}:80/".format(ip))

    counter = 0

def start():
    global ap
    global ip
    global udps
    global addr
    global counter
    global data
    global s
    global u

    try:
        while 1:

            u_data = u.read()
            if u_data != None:
                u_data = u_data.decode('utf-8')
                field = u_data.split(',')
                if len(field) >=2 :
                    blink(3)
                    ap.config(essid=field[0],authmode=1)
                    reconfig()
                    continue

            # DNS Loop 接收DNS请求
            # print("Before DNS...")
            try:
                data, addr = udps.recvfrom(1024) 	# 接受数据报
                # print("incomming datagram...")
                p=DNSQuery(data)					# 数据报DNS转发处理
                                                    # p.respuesta(ip)  返回转发后的IP(本机)
                udps.sendto(p.respuesta(ip), addr)	# 返回数据报
                print('Replying: {:s} -> {:s}'.format(p.dominio, ip))
            except:
                print("No dgram")
                pass

            # Web loop 接收HTTP请求
            # print("before accept...")
            try:
                res = s.accept()
                client_sock = res[0]
                client_addr = res[1]
                print("Client address:", client_addr)
                print("Client socket:", client_sock)

                client_stream = client_sock

                print("Request:")  # 获取HTTP请求头
                req = client_stream.readline() # 读第一行的
                print(req)
                while True:
                    h = client_stream.readline() # 挨个读下面的并打印，直达没有为止。
                    if h == b"" or h == b"\r\n" or h == None:
                        break
                    # print(h)
                
                # Change LED based on request variables
                request_url = req[4:-11] # 第一行的
                api = request_url[:5]
                if api == b'/led?':		 # 第一行判断路由
                    CONTENT.replace('[led]','/led')

                    
                client_stream.write(CONTENT)	# 返回HTTP respone

                client_stream.close()			# 关闭TCP连接
                counter += 1
            except:
                # 等待HTTP请求连接
                print("timeout for web... moving on...")
                pass
            # print("loop")
            time.sleep_ms(100)
    except KeyboardInterrupt:
        print('Closing')	# 异常关闭
        
    reconfig()
    start()

print('-open------')

blink(3)
reconfig()
start()
