micropython 在 esp8266 / esp32 上实现DNS服务器转发本机，以及强制门户验证和HTTP服务器  
captive.py 是原版的  
main.pu 是我个人修改过后的  
下面是原README.md  
------
# Captive Portal Demo
This is a simple captive portal demo for [MicroPython](http://micropython.org) using NodeMCU/ESP8266.

## Requirements
Needs RGB LED connected to ports 5, 4, 0 (These are ESP8266 port numbers not the NodeMCU ones)

## How to use it 

```
import captive
captive.start()
```

## Video demo

<iframe width="560" height="315" src="https://www.youtube.com/embed/gKbe48fQukc" frameborder="0" allowfullscreen></iframe>