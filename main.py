import enum
import time
import math
import random
import threading

import requests
from flask import Flask, request

from settings import COLORS, KITCHEN_HOSTNAME, KITCHEN_PORT, NR_OF_TABLES, TABLE_MINIMUM_WAITING_TIME, TABLE_MAXIMUM_WAITING_TIME, TIME_UNIT, DINING_HALL_PORT, MENU


flask_app = Flask(__name__)
table_state = [None]


class TableState(enum.Enum):
    FREE = 'FREE'
    WAIT_TO_ORDER = 'WAIT_TO_ORDER'
    WAIT_TO_BE_SERVED = 'WAIT_TO_BE_SERVED'


def dining_hall_print(msg, color=COLORS.OKBLUE):
    print(f'{color}|-- Dining Hall --->>> {msg}')


@flask_app.route('/distribution', methods=['POST'])
def post_order():
    request_body = request.get_json()
    dining_hall_print(request_body)
    table_state[request_body['table_id']] = TableState.FREE
    return {'status_code': 200}


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

    def run(self):
        while True:
            if table_state[self.table_id] == TableState.WAIT_TO_BE_SERVED:
                time.sleep(0.25 * TIME_UNIT)
                continue

            table_waiting_time = random.randint(
                TABLE_MINIMUM_WAITING_TIME, TABLE_MAXIMUM_WAITING_TIME) * TIME_UNIT
            time.sleep(table_waiting_time)
            self.make_order()

    def make_order(self):
        table_state[self.table_id] = TableState.WAIT_TO_BE_SERVED
        order_id = OrderId.next()
        _ = requests.post(
            url=f'http://{KITCHEN_HOSTNAME}:{KITCHEN_PORT}/order',
            json={
                "order_id": order_id,
                "table_id": self.table_id,
                "waiter_id": None,
                "items": [random.choice(list(MENU.keys())) for _ in range(3)],
                "priority": None,
                "max_wait": None,
                "pick_up_time": math.floor(time.time())
            })
        dining_hall_print(
            f'Table {self.table_id} has made an order with id {order_id}!!!')


if __name__ == '__main__':
    main_thread = threading.Thread(
        target=lambda: flask_app.run(
            host='0.0.0.0', port=DINING_HALL_PORT, debug=False, use_reloader=False)
    )

    threads = [main_thread]
    for i in range(1, NR_OF_TABLES + 1):
        table_thread = Table(i)
        threads.append(table_thread)
        table_state.append(TableState.FREE)

    for thread in threads:
        thread.start()
