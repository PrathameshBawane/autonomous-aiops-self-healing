from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import requests

log_path = os.path.join('logs', 'server.log')
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

def trigger_aiops():
    try:
        requests.post('http://localhost:8000/api/start', timeout=2)
        print("🤖 AIOps triggered!")
    except:
        pass

# ── REAL BUGS — not flags ──

@app.route('/')
def home():
    logging.info("Home visited")
    return jsonify({"status": "ok", "message": "Demo server running!"})

@app.route('/api/checkout', methods=['GET', 'POST'])
def checkout():
    # BUG 1: division by zero crashes checkout
    result = 100 / 0
    logging.info("Checkout success")
    return jsonify({"message": "Order placed!", "total": result}), 200

@app.route('/api/database', methods=['GET', 'POST'])
def database():
    # BUG 2: accessing undefined variable crashes database
    data = undefined_variable
    logging.info("Database success")
    return jsonify({"data": data}), 200

@app.route('/api/memory', methods=['GET', 'POST'])
def memory():
    # BUG 3: infinite list causes memory crash
    big_list = []
    for i in range(10000000):
        big_list.append(i * "x")
    return jsonify({"memory": "ok"}), 200

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"server": "demo_server", "status": "running"})

# when patch get approve it replace the patch code 
@app.route('/api/heal', methods=['POST'])  
def heal():
    return jsonify({"message": "Heal endpoint ready"}), 200

if __name__ == '__main__':
    logging.info("Demo server starting...")
    print("🚀 Demo server on port 5003...")
    app.run(host='0.0.0.0', debug=True, port=5003,use_reloader=False)