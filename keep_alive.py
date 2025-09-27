from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Keep-alive server is running."

def keep_alive(app_instance):
    def run():
        app_instance.run(host='0.0.0.0', port=10000)
    thread = threading.Thread(target=run)
    thread.start()
