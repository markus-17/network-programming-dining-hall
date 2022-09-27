import threading
import itertools

from Table import Table
from Waiter import Waiter
from FlaskApp import flask_app
from utils import waiter_threads, table_threads
from settings import NR_OF_TABLES, DINING_HALL_PORT, NR_OF_WAITERS


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
