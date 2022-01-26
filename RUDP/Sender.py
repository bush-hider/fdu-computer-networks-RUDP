import sys
import getopt

import Checksum
import BasicSender
import Checksum
import BasicSender
import base64
import time
from copy import deepcopy

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.PacketDataSize = 500  # packet size
        self.BufSize = 5
        self.Buf = dict()
        self.TimeOut = 0.5
        self.seqno = 0
        self.MaxAck = 0
        self.firstTag = True
        self.endTag = False
        self.LastSendTime = time.time()
        self.acks = [] # 用于选择重传，记录选择的确认

    '''
    思路:维护一个大小为BufSize的缓冲区,实现(通过dict):{seqno,packet}
    (1)开始时，把缓冲区读满，发送全部内容，然后接受ACK，检查接收的最大ACK是否满足预期。正确则开始下一轮，否则超时:
    (2)超时处理:分为GBN和SR两种方式，共同点是根据接收到TimeOut时间内接受的信息更新缓冲区(删掉被确认的部分信息，重
    新用需要发送的信息填满缓冲区)，发送、接受ACK，检查接收的最大ACK是否满足预期，不满足则继续超时处理。

    总结以上两个方面，具体实现为一个大while循环，每次开始时构造缓冲区Buf，构造方式分别为无错、GBN、SR，后两种构造方式
    对应超时重传。构造完成后，将缓冲区内容发送、等待接受，然后检查是否有错，继续循环。
    '''
    # Main sending loop.
    def BuildBuf_ToMaxSize(self):
        while len(self.Buf) < self.BufSize and not self.endTag:
            msg = self.infile.read(self.PacketDataSize)
            msg = base64.b64encode(msg).decode()
            # 根据情况选择类型后make_packet
            if(self.firstTag):
                packet = self.make_packet('start', self.seqno, msg)
                self.firstTag = False
            elif(msg == '' or msg == ""):
                packet = self.make_packet('end', self.seqno, msg)
                self.endTag = True
            else:
                packet = self.make_packet('data', self.seqno, msg)
            self.Buf.update({self.seqno: packet})
            self.seqno += 1

    def GBN_BuildBuf(self):
        # 缓冲区中 seqno < MaxAck 的包被丢弃，其余包需要重传;
        tmp = deepcopy(self.Buf)
        for key in tmp.keys():
            if(int(key) < self.MaxAck):
                self.Buf.pop(key)
        # 扩充缓冲区至BufSize:
        self.BuildBuf_ToMaxSize()
    
    def SR_BuildBuf(self):
        # 缓冲区中 seqno < MaxAck 的包被丢弃、被选择确认的包(self.acks)要丢弃;
        # 丢弃 seqno < MaxAck 的包:
        tmp = deepcopy(self.Buf)
        for key in tmp.keys():
            if(int(key) < self.MaxAck):
                self.Buf.pop(key)
        # 丢弃被选择确认的包: 
        tmp = deepcopy({key:self.Buf[key] for key in self.Buf.keys() - set(self.acks)})
        self.Buf = deepcopy(tmp)
        self.acks.clear()
        # 扩充缓冲区至BufSize:
        self.BuildBuf_ToMaxSize()

    def start(self):
        REsendTag = False
        while True:
            # build BUf
            if(REsendTag == False):
                self.BuildBuf_ToMaxSize()
            else:
                if(self.sackMode == False):
                    self.GBN_BuildBuf()
                else:
                    self.SR_BuildBuf()
            # send BUf
            for key,value in self.Buf.items():
                if int(key) < self.MaxAck:
                    continue
                # debug: print("send:",key)
                self.send("{}".format(value))
            # receive answer
            i = 1
            self.LastSendTime = time.time()
            while i <= len(self.Buf):
                if time.time() - self.LastSendTime > self.TimeOut:
                    break
                try:
                    response = self.receive(self.TimeOut/2)
                except:
                    continue
                i += 1
                if response == None:
                    continue
                response = response.decode()
                if not Checksum.validate_checksum(response):
                    continue
                splitResponse = self.split_packet(response)
                if(self.sackMode == False):
                    # 不使用选择重传
                    if int(splitResponse[1]) > self.MaxAck:
                        self.MaxAck = int(splitResponse[1])
                else:
                    # 选择重传
                    split_ = splitResponse[1].split(';')
                    if int(split_[0]) > self.MaxAck: 
                        self.MaxAck = int(split_[0])
                    # '选择确认'加入列表self.acks:
                    try:
                        sack_acks = split_[1].split(',')
                        for sack_ack in sack_acks:
                            self.acks.append(int(sack_ack))  
                    except:
                        continue  
                    
            # 检查是否需要重传，设置REsendTag
            if(self.MaxAck < self.seqno):
                REsendTag = True
            else:
                REsendTag = False
                self.Buf.clear()
            if(self.endTag and len(self.Buf) == 0):
                break
        self.infile.close()


    def handle_timeout(self):
        pass

    def handle_new_ack(self, ack):
        pass

    def handle_dup_ack(self, ack):
        pass

    def log(self, msg):
        if self.debug:
            print(msg)


'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print("RUDP Sender")
        print("-f FILE | --file=FILE The file to transfer; if empty reads from STDIN")
        print("-p PORT | --port=PORT The destination port, defaults to 33122")
        print("-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost")
        print("-d | --debug Print debug messages")
        print("-h | --help Print this usage message")
        print("-k | --sack Enable selective acknowledgement mode")

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
