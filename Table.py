import math
import time
import queue
import random
import threading
from statistics import mean

from utils import reviews, OrderId, wait_to_make_order_queue
from settings import dining_hall_print, TABLE_MAXIMUM_WAITING_TIME, TABLE_MINIMUM_WAITING_TIME, TIME_UNIT, MENU


class Table(threading.Thread):
    def __init__(self, table_id, *args, **kwargs):
        super(Table, self).__init__(*args, **kwargs)
        self.table_id = table_id
        self.__prepared_orders_queue = queue.Queue()

    def run(self):
        while True:
            dining_hall_print(f'Table_{self.table_id} is FREE')
            table_waiting_time = random.randint(
                TABLE_MINIMUM_WAITING_TIME, TABLE_MAXIMUM_WAITING_TIME) * TIME_UNIT
            time.sleep(table_waiting_time)

            dining_hall_print(f'Table_{self.table_id} is WAITING TO ORDER')
            wait_to_make_order_queue.put(self.table_id)

            # An Waiter should get the table_id from the wait_to_make_order_queue
            # and call make_order method

            # The following line will block the thread until
            # the Waiter will put the prepared order in self.__prepared_orders_queue
            prepared_order = self.__prepared_orders_queue.get()
            ratio = prepared_order['cooking_time'] / prepared_order['max_wait']
            stars = 0
            if ratio <= 1.4:
                stars = 1
            if ratio <= 1.3:
                stars = 2
            if ratio <= 1.2:
                stars = 3
            if ratio <= 1.1:
                stars = 4
            if ratio <= 1.0:
                stars = 5
            reviews.append(stars)
            dining_hall_print(f'Table_{prepared_order["table_id"]} served by Waiter_{prepared_order["waiter_id"]} rated Order_{prepared_order["order_id"]} with {stars} stars (Average {mean(reviews)} stars)')

    def make_order(self):
        order_id = OrderId.next()
        items = [random.choice(list(MENU.keys())) for _ in range(random.randint(1, 5))]
        max_wait_time = 1.3 * max(MENU[food_id]["preparation-time"] for food_id in items)
        priority = sum(MENU[item]["preparation-time"] for item in items)
        order = {
            "order_id": order_id,
            "table_id": self.table_id,
            "waiter_id": None,
            "items": items,
            "priority": priority,
            "max_wait": max_wait_time,
            "pick_up_time": math.floor(time.time())
        }
        return order

    def serve_order(self, prepared_order):
        self.__prepared_orders_queue.put(prepared_order)
