### README

##### 简介

复旦大学基于UDP实现可靠传输实验，框架为：RUDP_python3_框架.zip

框架提供接收端和测试环境，注意根据接收端写发送端。

Sender.py ——发送端，包括GBN和SR两种方式。

tests ——丢包、失序等测试。

此外 BasicSender.py 和 Receiver.py 有局部的修改，以支持任意文件类型。

##### RUDP协议

发送端：

start|<sequence number>|<data>|<checksum>

data|<sequence number>|<data>|<checksum>

end|<sequence number>|<data>|<checksum>

接收端（GBN）：

ack|<sequence number>|<checksum>

接收端（SR）：

sack|<cum_ack;sack1,sack2,sack3,...>|<checksum>

注：cum_ack相当于GBN下的sequence number

##### 实验环境

Ubuntu 18.04.6 LTS + python 3.6.9

 （请在linux环境下运行测试，windos下存在系统中断测试的情况）

##### 运行测试

- 简单传输：

  Go-Back-N接收端：python Receiver.py

  Go-Back-N发送端：python Sender.py -f <file name>

  选择重传接收端：python Receiver.py -k

  选择重传发送端：python Sender.py -f <file name> -k

- 测试 - 默认文件(README)：

​       python TestHarness.py -s Sender.py -r Receiver.py

- 测试 - 目录下指定文件（需修改TestHarness.py代码）：

​       python TestHarness.py -s Sender.py -r Receiver.py -f filename