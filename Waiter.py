import queue
import threading

import requests

from utils import table_threads, wait_to_make_order_queue
from settings import TIME_UNIT, WAITER_TIME_TO_POST_ORDER, KITCHEN_HOSTNAME, KITCHEN_PORT, dining_hall_print


class Waiter(threading.Thread):
    def __init__(self, waiter_id: int, *args, **kwargs):
        super(Waiter, self).__init__(*args, **kwargs)
        self.waiter_id: int = waiter_id
        self.__prepared_orders_queue: queue.Queue = queue.Queue()

    def run(self):
        while True:
            try:
                prepared_order = self.__prepared_orders_queue.get(
                    timeout=(WAITER_TIME_TO_POST_ORDER * TIME_UNIT))
                table_threads[prepared_order['table_id']].serve_order(prepared_order)
            except queue.Empty:
                # there was no order to be served for WAITER_TIME_TO_POST_ORDER Time units, do nothing
                pass

            try:
                table_id = wait_to_make_order_queue.get_nowait()
                order = table_threads[table_id].make_order()
                order["waiter_id"] = self.waiter_id
                requests.post(
                    url=f'http://{KITCHEN_HOSTNAME}:{KITCHEN_PORT}/order',
                    json=order
                )
                dining_hall_print(
                    f'Table_{order["table_id"]} using Waiter_{order["waiter_id"]} create Order_{order["order_id"]}'
                )
            except queue.Empty:
                # No table wants to make order, do nothing
                pass

    def add_prepared_order(self, prepared_order):
        self.__prepared_orders_queue.put(prepared_order)
