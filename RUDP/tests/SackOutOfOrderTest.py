import random

from tests.BasicTest import BasicTest

class SackOutOfOrderTest(BasicTest):
    def __init__(self, forwarder, input_file):
        super(SackOutOfOrderTest, self).__init__(forwarder, input_file, sackMode = True)

    def handle_packet(self):
        random.shuffle(self.forwarder.in_queue)
        self.forwarder.out_queue = self.forwarder.in_queue
        self.forwarder.in_queue = []
