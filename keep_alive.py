from threading import Thread

def keep_alive(app):  
    def run():
        app.run(host='0.0.0.0', port=8080)
    t = Thread(target=run)
    t.start()
