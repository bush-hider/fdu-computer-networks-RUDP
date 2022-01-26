import random

from tests.BasicTest import BasicTest

class OutOfOrderTest(BasicTest):
    def handle_packet(self):
        random.shuffle(self.forwarder.in_queue)
        self.forwarder.out_queue = self.forwarder.in_queue
        self.forwarder.in_queue = []
