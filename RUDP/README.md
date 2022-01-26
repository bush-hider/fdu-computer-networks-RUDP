### README

(1) 环境：

Ubuntu 18.04.6 LTS + python 3.6.9

 （请在linux环境下运行测试，windos下存在系统中断测试的情况）

(2) 测试：

- 默认文件(README)：

​    python TestHarness.py -s Sender.py -r Receiver.py

- 目录下指定文件：

​    python TestHarness.py -s Sender.py -r Receiver.py -f filename