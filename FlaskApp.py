from flask import Flask, request

from utils import waiter_threads


flask_app = Flask(__name__)

@flask_app.route('/distribution', methods=['POST'])
def post_order():
    prepared_order = request.get_json()
    waiter_threads[prepared_order['waiter_id']].add_prepared_order(prepared_order)
    return {'status_code': 200}
