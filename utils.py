import queue
import threading


reviews = []
waiter_threads = {}
table_threads = {}
wait_to_make_order_queue = queue.Queue()

class OrderId:
    __value = 0
    __lock = threading.Lock()

    @staticmethod
    def next():
        with OrderId.__lock:
            OrderId.__value += 1
            return OrderId.__value