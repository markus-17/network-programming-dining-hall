import time
import math
import random
import queue
import threading
import itertools

import requests
from flask import Flask, request

from settings import COLORS, KITCHEN_HOSTNAME, KITCHEN_PORT, NR_OF_TABLES, TABLE_MINIMUM_WAITING_TIME, TABLE_MAXIMUM_WAITING_TIME, TIME_UNIT, DINING_HALL_PORT, MENU, NR_OF_WAITERS


# Gloabl Variables
flask_app = Flask(__name__)
waiter_threads = {}
table_threads = {}
wait_to_make_order_queue = queue.Queue()


def dining_hall_print(msg, color=COLORS.OKBLUE):
    print(f'{color}|-- Dining Hall --->>> {msg}')


@flask_app.route('/distribution', methods=['POST'])
def post_order():
    prepared_order = request.get_json()
    waiter_threads[prepared_order['waiter_id']].add_prepared_order(prepared_order)
    return {'status_code': 200}


class Waiter(threading.Thread):
    def __init__(self, waiter_id: int, *args, **kwargs):
        super(Waiter, self).__init__(*args, **kwargs)
        self.waiter_id: int = waiter_id
        self.__prepared_orders_queue: queue.Queue = queue.Queue()

    def run(self):
        while True:
            try:
                prepared_order = self.__prepared_orders_queue.get(
                    timeout=(3 * TIME_UNIT))
                table_threads[prepared_order['table_id']].serve_order(prepared_order)
            except queue.Empty:
                # there was no order to be served for 3 Time units, do nothing
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


class OrderId:
    __value = 0
    __lock = threading.Lock()

    @staticmethod
    def next():
        with OrderId.__lock:
            OrderId.__value += 1
            return OrderId.__value


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
            dining_hall_print(f'Table_{prepared_order["table_id"]} served by Waiter_{prepared_order["waiter_id"]} rated Order_{prepared_order["order_id"]} with NOT_COMPUTED stars.')

    def make_order(self):
        order_id = OrderId.next()
        order = {
            "order_id": order_id,
            "table_id": self.table_id,
            "waiter_id": None,
            "items": [random.choice(list(MENU.keys())) for _ in range(3)],
            "priority": None,
            "max_wait": None,
            "pick_up_time": math.floor(time.time())
        }
        return order

    def serve_order(self, prepared_order):
        self.__prepared_orders_queue.put(prepared_order)


if __name__ == '__main__':
    server_thread = threading.Thread(
        target=lambda: flask_app.run(
            host='0.0.0.0', port=DINING_HALL_PORT, debug=False, use_reloader=False)
    )

    for i in range(1, NR_OF_WAITERS + 1):
        waiter_threads[i] = Waiter(waiter_id=i)

    for i in range(1, NR_OF_TABLES + 1):
        table_threads[i] = Table(table_id=i)

    for thread in itertools.chain([server_thread], waiter_threads.values(), table_threads.values()):
        thread.start()
